from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from dev.models import Profile, Project as DevProject
from .models import CustomerProfile, Project, ProjectRequest, DeveloperRequest, MeetingRequest
from dev.models import Comment
from .forms import CustomerProfileForm, ProjectForm
from django.conf import settings
from django.contrib import messages
import uuid
from django.http import JsonResponse

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
    developers = Profile.objects.filter(is_available=True)
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
    developer = get_object_or_404(Profile, id=dev_id)
    comments = Comment.objects.filter(profile=developer).order_by('-created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                profile=developer,
                author=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('customer:developer_profile', dev_id=dev_id)
    
    return render(request, 'customer/developer_profile.html', {
        'developer': developer,
        'comments': comments
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
def request_developer(request, dev_id, project_id=None):
    try:
        developer = get_object_or_404(Profile, id=dev_id)
        
        if request.method == 'POST':
            message = request.POST.get('message')
            project = get_object_or_404(Project, id=project_id, customer=request.user.customerprofile)
            
            # Check if request already exists
            existing_request = DeveloperRequest.objects.filter(
                customer=request.user.customerprofile,
                developer=developer,
                project=project
            ).first()
            
            if existing_request:
                messages.warning(request, 'You have already sent a request to this developer for this project.')
            else:
                # Create developer request
                DeveloperRequest.objects.create(
                    customer=request.user.customerprofile,
                    developer=developer,
                    project=project,
                    message=message
                )
                messages.success(request, 'Request sent to developer successfully!')
            
            return redirect('customer:browse_developers')
            
        projects = Project.objects.filter(
            customer=request.user.customerprofile,
            status='open'
        )
        return render(request, 'customer/request_developer.html', {
            'developer': developer,
            'projects': projects
        })
        
    except Profile.DoesNotExist:
        print("Developer profile not found.")
        messages.error(request, 'Developer profile not found.')
        return redirect('customer:browse_developers')

@login_required
def request_meeting(request, dev_id):
    developer = get_object_or_404(Profile, id=dev_id)
    
    if request.method == 'POST':
        # Create a unique room ID
        room_id = str(uuid.uuid4())
        
        meeting = MeetingRequest.objects.create(
            customer=request.user,
            developer=developer,
            room_id=room_id,
            status='pending'
        )
        
        messages.success(request, 'Meeting request sent successfully!')
        return redirect('customer:developer_profile', dev_id=dev_id)
        
    return render(request, 'customer/request_meeting.html', {
        'developer': developer
    })

@login_required
def join_meeting(request, meeting_id):
    meeting = get_object_or_404(MeetingRequest, id=meeting_id, 
                              customer=request.user, status='accepted')
    
    context = {
        'room_id': meeting.room_id,
        'user_name': request.user.get_full_name() or request.user.username,
    }
    
    return render(request, 'customer/meeting_room.html', context)

@login_required
def check_developer_availability(request, dev_id):
    try:
        developer = get_object_or_404(Profile, id=dev_id)
        is_available = developer.is_currently_available()
        
        response_data = {
            'available': is_available,
            'status': 'available' if is_available else 'unavailable'
        }
        
        # If manually available, include end time
        if is_available and developer.manual_availability and developer.manual_availability_end:
            response_data['ends_at'] = developer.manual_availability_end.isoformat()
            
        return JsonResponse(response_data)
        
    except Profile.DoesNotExist:
        return JsonResponse({
            'error': 'Developer not found'
        }, status=404)



class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'dev/project_detail.html'
    context_object_name = 'project'

@login_required
def developer_project_detail(request, dev_id, project_id):
    developer = get_object_or_404(Profile, id=dev_id)
    project = get_object_or_404(DevProject, id=project_id, profile=developer)
    
    return render(request, 'customer/project_detail.html', {
        'project': project,
        'developer': developer
    })