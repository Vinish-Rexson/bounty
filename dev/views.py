from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProfileForm, ProjectForm
from .models import Profile, Project
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from customer.models import Project, ProjectRequest

def is_developer(user):
    return user.groups.filter(name=settings.DEVELOPER_GROUP).exists()

developer_required = user_passes_test(is_developer, login_url='login')

@developer_required
@login_required
def dashboard(request):
    profile = request.user.profile
    comments = profile.comments.all().order_by('-created_at')
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get only customer-initiated requests
    customer_requests = ProjectRequest.objects.filter(
        developer=profile,
        status='pending',
        initiated_by_customer=True  # Only show requests initiated by customers
    ).select_related('project', 'project__customer', 'project__customer__user')
    
    # Get only developer-initiated requests
    pending_requests = ProjectRequest.objects.filter(
        developer=profile,
        status='pending',
        initiated_by_customer=False  # Only show requests initiated by developers
    ).select_related('project')
    
    context = {
        'user': request.user,
        'profile': profile,
        'active_projects': ProjectRequest.objects.filter(
            developer=profile,
            status='accepted'
        ).select_related('project'),
        'customer_requests': customer_requests,
        'pending_requests': pending_requests,
    }
    return render(request, 'dev/dashboard.html', {
        'profile': profile,
        'comments': comments
    }, context)

@developer_required
@login_required
def profile(request):
    try:
        profile = request.user.profile
        # Get projects ordered by creation date
        projects = profile.projects.all().order_by('-created_at')
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
        projects = []
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Update required fields to match our new field names
            required_fields = [
                'display_name', 'title', 'years_of_experience', 
                'hourly_rate', 'github_url', 'timezone'
            ]
            
            # Check availability fields based on type
            availability_type = form.cleaned_data['availability_type']
            if availability_type == 'weekday':
                required_fields.extend(['weekday_from', 'weekday_to'])
            elif availability_type == 'weekend':
                required_fields.extend(['weekend_from', 'weekend_to'])
            else:  # temporary
                required_fields.extend(['temp_from', 'temp_to'])
            
            is_complete = all(getattr(profile, field) for field in required_fields)
            
            if is_complete and form.cleaned_data['skills']:
                profile.is_profile_completed = True
                profile.is_verified = True  # Auto-verify when profile is complete
            
            profile.save()
            form.save_m2m()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('dev:dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'dev/profile.html', {
        'form': form,
        'profile': profile,
        'projects': projects
    })

def home(request):
    return render(request, 'dev/index.html')

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dev/project_form.html'
    success_url = reverse_lazy('dev:profile')

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'dev/project_detail.html'
    context_object_name = 'project'

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'dev/project_form.html'

@require_http_methods(["POST"])
@login_required
def project_create_api(request):
    data = json.loads(request.body)
    project = Project.objects.create(
        name=data['name'],
        readme=data['readme'],
        deployed_url=data['deployed_url'],
        github_url=data['github_url'],
        client=data['client'],
        profile=request.user.profile
    )
    
    return JsonResponse({
        'id': project.id,
        'name': project.name,
        'client': project.client
    })

@developer_required
@login_required
def browse_projects(request):
    projects = Project.objects.filter(status='open')
    developer = Profile.objects.get(user=request.user)
    
    # Get the status of requests for each project
    for project in projects:
        try:
            request_status = ProjectRequest.objects.get(
                project=project, 
                developer=developer
            ).status
        except ProjectRequest.DoesNotExist:
            request_status = None
        project.request_status = request_status
    
    return render(request, 'dev/browse_projects.html', {'projects': projects})

@developer_required
@login_required
def request_project(request, project_id):
    if request.method == 'POST':
        project = Project.objects.get(id=project_id)
        developer = Profile.objects.get(user=request.user)
        message = request.POST.get('message', '')
        
        # Check if any request already exists (from either party)
        existing_request = ProjectRequest.objects.filter(
            project=project,
            developer=developer
        ).first()
        
        if existing_request:
            if existing_request.initiated_by_customer:
                messages.info(request, 'The customer has already sent you a request for this project')
            else:
                messages.warning(request, 'You have already requested this project')
        else:
            # Create only the developer's request
            ProjectRequest.objects.create(
                project=project,
                developer=developer,
                message=message,
                initiated_by_customer=False,  # This marks it as a developer request
                status='pending'
            )
            messages.success(request, 'Request sent successfully!')
        
        return redirect('dev:dashboard')
    
    return redirect('dev:browse_projects')

@developer_required
@login_required
def handle_customer_request(request, request_id):
    if request.method == 'POST':
        project_request = ProjectRequest.objects.get(
            id=request_id,
            developer=request.user.profile
        )
        action = request.POST.get('action')
        
        if action == 'accept':
            project_request.status = 'accepted'
            project_request.project.assigned_developer = request.user.profile
            project_request.project.status = 'in_progress'
            project_request.project.save()
            
            # Reject all other requests for this project
            ProjectRequest.objects.filter(
                project=project_request.project
            ).exclude(id=request_id).update(status='rejected')
            
            messages.success(request, 'You have accepted the project request.')
        
        elif action == 'reject':
            project_request.status = 'rejected'
            messages.info(request, 'You have declined the project request.')
        
        project_request.save()
        
    return redirect('dev:dashboard')