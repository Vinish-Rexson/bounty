from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from dev.models import Profile as DevProfile
from .models import CustomerProfile, Project, ProjectRequest
from .forms import CustomerProfileForm, ProjectForm
from django.conf import settings
from django.contrib import messages

def is_customer(user):
    return user.groups.filter(name=settings.CUSTOMER_GROUP).exists()

customer_required = user_passes_test(is_customer, login_url='login')

@customer_required
@login_required
def dashboard(request):
    customer_profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    projects = Project.objects.filter(customer=customer_profile)
    return render(request, 'customer/dashboard.html', {
        'projects': projects
    })

@customer_required
@login_required
def browse_developers(request):
    developers = DevProfile.objects.filter(is_available=True)
    project_id = request.GET.get('project_id')
    project = None
    
    if project_id:
        project = Project.objects.get(id=project_id)
        
        # Get existing requests for each developer
        for developer in developers:
            try:
                request_status = ProjectRequest.objects.get(
                    project=project,
                    developer=developer
                ).status
            except ProjectRequest.DoesNotExist:
                request_status = None
            developer.request_status = request_status
    
    return render(request, 'customer/browse_developers.html', {
        'developers': developers,
        'project': project
    })

@login_required
def developer_profile(request, dev_id):
    developer = DevProfile.objects.get(id=dev_id)
    return render(request, 'customer/developer_profile.html', {
        'developer': developer
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            customer_profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
            project.customer = customer_profile
            project.save()
            form.save_m2m()
            return redirect('customer:dashboard')
    else:
        form = ProjectForm()
    return render(request, 'customer/create_project.html', {'form': form})

@customer_required
@login_required
def project_requests(request, project_id):
    project = Project.objects.get(id=project_id)
    # Only show developer-initiated requests in the project requests view
    requests = ProjectRequest.objects.filter(
        project=project,
        initiated_by_customer=False  # Only show requests from developers
    ).select_related('developer')
    
    return render(request, 'customer/project_requests.html', {
        'requests': requests, 
        'project': project
    })

@customer_required
@login_required
def handle_request(request, request_id):
    if request.method == 'POST':
        project_request = ProjectRequest.objects.get(id=request_id)
        action = request.POST.get('action')
        
        if action == 'accept':
            project_request.status = 'accepted'
            project_request.project.assigned_developer = project_request.developer
            project_request.project.status = 'in_progress'
            project_request.project.save()
            
            # Reject all other requests
            ProjectRequest.objects.filter(
                project=project_request.project
            ).exclude(id=request_id).update(status='rejected')
            
        elif action == 'reject':
            project_request.status = 'rejected'
            
        project_request.save()
        messages.success(request, f'Request {action}ed successfully!')
        
    return redirect('customer:project_requests', project_id=project_request.project.id)

@customer_required
@login_required
def request_developer(request, project_id, developer_id):
    if request.method == 'POST':
        project = Project.objects.get(id=project_id)
        developer = DevProfile.objects.get(id=developer_id)
        message = request.POST.get('message', '')
        
        print(f"Customer requesting developer: {developer.display_name}")
        print(f"For project: {project.title}")
        
        # Check existing requests
        existing_requests = ProjectRequest.objects.filter(
            project=project,
            developer=developer
        )
        
        print(f"Existing requests found: {existing_requests.count()}")
        for req in existing_requests:
            print(f"Request ID: {req.id}, Initiated by customer: {req.initiated_by_customer}")
        
        if existing_requests.exists():
            existing_request = existing_requests.first()
            if existing_request.initiated_by_customer:
                messages.warning(request, f'You have already sent a request to {developer.display_name}')
            else:
                messages.info(request, f'{developer.display_name} has already requested this project')
        else:
            new_request = ProjectRequest.objects.create(
                project=project,
                developer=developer,
                message=message,
                initiated_by_customer=True,
                status='pending'
            )
            print(f"Created new request ID: {new_request.id}")
            messages.success(request, f'Request sent to {developer.display_name}')
        
        return redirect('customer:dashboard')
    
    return redirect('customer:browse_developers')
