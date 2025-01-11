from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from .forms import ProfileForm, ProjectForm
from .models import Profile, Project
from django.contrib import messages
from django.conf import settings
from customer.models import Project, ProjectRequest, DeveloperRequest
from django.http import JsonResponse




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


def is_developer(user):
    return user.groups.filter(name=settings.DEVELOPER_GROUP).exists()

developer_required = user_passes_test(is_developer, login_url='login')

@developer_required
@login_required
def dashboard(request):
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    comments = profile.comments.all().order_by('-created_at')
    
    # Get customer requests
    customer_requests = DeveloperRequest.objects.filter(
        developer=profile,
        status='pending'
    ).select_related('project')
    
    # Get pending requests
    pending_requests = ProjectRequest.objects.filter(
        developer=profile,
        status='pending'
    ).select_related('project')
    
    context = {
        'user': request.user,
        'profile': profile,
        'comments': comments,
        'active_projects': ProjectRequest.objects.filter(
            developer=profile,
            status='accepted'
        ).select_related('project'),
        'customer_requests': customer_requests,
        'pending_requests': pending_requests,
    }
    return render(request, 'dev/dashboard.html', context)

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

@developer_required
@login_required
def browse_projects(request):
    projects = Project.objects.filter(status='open')
    return render(request, 'dev/browse_projects.html', {
        'projects': projects
    })

@developer_required
@login_required
def request_project(request, project_id):
    if request.method == 'POST':
        project = Project.objects.get(id=project_id)
        message = request.POST.get('message', '')
        
        # Create project request
        ProjectRequest.objects.create(
            project=project,
            developer=request.user.profile,
            message=message
        )
        
        messages.success(request, 'Project request sent successfully!')
        return redirect('dev:browse_projects')
        
    project = Project.objects.get(id=project_id)
    return render(request, 'dev/request_project.html', {'project': project})

@developer_required
@login_required
def view_requests(request):
    requests = DeveloperRequest.objects.filter(developer=request.user.profile)
    return render(request, 'dev/view_requests.html', {'requests': requests})

@developer_required
@login_required
def handle_request(request, request_id):
    if request.method == 'POST':
        dev_request = DeveloperRequest.objects.get(id=request_id)
        action = request.POST.get('action')
        
        if action == 'accept':
            dev_request.status = 'accepted'
            dev_request.project.status = 'in_progress'
            dev_request.project.assigned_developer = request.user.profile
            dev_request.project.save()
        elif action == 'reject':
            dev_request.status = 'rejected'
            
        dev_request.save()
        messages.success(request, f'Request {action}ed successfully!')
        
    return redirect('dev:view_requests')

@developer_required
@login_required
def project_create_api(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.developer = request.user.profile
            project.save()
            return JsonResponse({'status': 'success', 'id': project.id})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@developer_required
@login_required
def handle_customer_request(request, request_id):
    developer_request = get_object_or_404(DeveloperRequest, id=request_id, developer=request.user.profile)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            # Update the developer request status
            developer_request.status = 'accepted'
            
            # Update the project status and assign the developer
            project = developer_request.project
            project.status = 'in_progress'  # or whatever status you use for active projects
            project.assigned_developer = request.user.profile
            project.save()
            
            # Reject all other pending requests for this project
            DeveloperRequest.objects.filter(
                project=project,
                status='pending'
            ).exclude(id=request_id).update(status='rejected')
            
            messages.success(request, 'Request accepted successfully!')
            
        elif action == 'reject':
            developer_request.status = 'rejected'
            messages.success(request, 'Request rejected successfully!')
        
        developer_request.save()
        
    return redirect('dev:dashboard')

@developer_required
@login_required
def projects(request):
    # Get all projects associated with the developer
    projects = Project.objects.filter(
        assigned_developer=request.user.profile
    ).order_by('-created_at')
    
    return render(request, 'dev/projects.html', {
        'projects': projects
    })

@developer_required
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, assigned_developer=request.user.profile)
    return render(request, 'dev/project_detail.html', {
        'project': project
    })


# X-X-X-X-X-X-X-X-X-X-X-X-this is for dev side projects X-X-X-X-X-X-X-X-X-X-X
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

@require_http_methods(["POST"])
@login_required
def project_update_api(request, pk):
    project = get_object_or_404(Project, pk=pk, profile=request.user.profile)
    
    print("="*50)
    print("Received POST request for project update")
    print(f"Project ID: {pk}")
    
    try:
        # Clean up URLs if they don't have http:// or https://
        post_data = request.POST.copy()  # Make a mutable copy
        for field in ['deployed_url', 'github_url']:
            if post_data.get(field) and not post_data[field].startswith(('http://', 'https://')):
                post_data[field] = 'https://' + post_data[field]
        
        form = ProjectForm(post_data, instance=project)
        print("Form data after URL cleanup:")
        print(form.data)
        print("Form is valid:", form.is_valid())
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            messages.error(request, f'Validation error: {form.errors}')
        else:
            project = form.save()
            print("Project saved successfully:", project)
            messages.success(request, 'Project updated successfully!')
            
    except Exception as e:
        print("Exception occurred:", str(e))
        print("Exception type:", type(e))
        messages.error(request, f'Error updating project: {str(e)}')
    
    return redirect('dev:dev_project_detail', pk=project.pk)

# X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X