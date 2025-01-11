from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ProfileForm, ProjectForm
from .models import Profile, Project
from django.contrib import messages
from django.conf import settings
from customer.models import Project, ProjectRequest, DeveloperRequest

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