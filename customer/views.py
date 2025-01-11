from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from dev.models import Profile as DevProfile
from .models import CustomerProfile, Project, ProjectRequest, DeveloperRequest
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
    developers = DevProfile.objects.filter(is_verified=True, is_available=True)
    return render(request, 'customer/browse_developers.html', {
        'developers': developers
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
    project = Project.objects.get(id=project_id, customer=request.user.customerprofile)
    requests = project.requests.all()
    return render(request, 'customer/project_requests.html', {
        'project': project,
        'requests': requests
    })

@customer_required
@login_required
def handle_request(request, request_id):
    if request.method == 'POST':
        project_request = ProjectRequest.objects.get(id=request_id)
        action = request.POST.get('action')
        
        if action == 'accept':
            project_request.status = 'accepted'
            project_request.project.status = 'in_progress'
            project_request.project.assigned_developer = project_request.developer
            project_request.project.save()
            
            # Reject other requests
            project_request.project.requests.exclude(id=request_id).update(status='rejected')
            
        elif action == 'reject':
            project_request.status = 'rejected'
            
        project_request.save()
        messages.success(request, f'Request {action}ed successfully!')
        
    return redirect('customer:project_requests', project_id=project_request.project.id)

@customer_required
@login_required
def request_developer(request, dev_id):
    if request.method == 'POST':
        developer = DevProfile.objects.get(id=dev_id)
        project_id = request.POST.get('project')
        message = request.POST.get('message')
        
        project = Project.objects.get(id=project_id, customer=request.user.customerprofile)
        
        # Create developer request
        DeveloperRequest.objects.create(
            customer=request.user.customerprofile,
            developer=developer,
            project=project,
            message=message
        )
        
        messages.success(request, 'Request sent to developer successfully!')
        return redirect('customer:browse_developers')
        
    developer = DevProfile.objects.get(id=dev_id)
    projects = Project.objects.filter(
        customer=request.user.customerprofile,
        status='open'
    )
    return render(request, 'customer/request_developer.html', {
        'developer': developer,
        'projects': projects
    })
