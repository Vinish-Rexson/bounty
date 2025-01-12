from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from customer.models import CustomerProfile, Project, MeetingRequest
from dev.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from customer.models import ProjectStatusRequest

@login_required
def chat_room(request, room_id):
    # First try to get the project
    project = get_object_or_404(Project, id=room_id)
    
    # Try to get existing chat room first
    chat_room = ChatRoom.objects.filter(
        Q(customer=project.customer.user, developer=project.assigned_developer.user, project=project) |
        Q(developer=project.customer.user, customer=project.assigned_developer.user, project=project)
    ).first()
    
    # If no chat room exists, create one
    if not chat_room:
        chat_room = ChatRoom.objects.create(
            customer=project.customer.user,
            developer=project.assigned_developer.user,
            project=project
        )
    
    # Get messages for this room
    messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    # Determine if the user can request a meeting
    is_customer = hasattr(request.user, 'customerprofile')
    can_request_meeting = not is_customer and project and project.status == 'in_progress'
    
    active_meeting = MeetingRequest.objects.filter(
        room_id=chat_room.id,
        status='accepted',
        created_at__gte=timezone.now() - timezone.timedelta(hours=24)
    ).first()
    
    # Determine user type and project status request visibility
    is_customer = hasattr(request.user, 'customerprofile')
    is_developer = hasattr(request.user, 'profile')
    
    project_status_request = None
    can_approve_request = False
    
    if chat_room.project:
        project_status_request = ProjectStatusRequest.objects.filter(
            project=chat_room.project,
            is_approved=False
        ).first()
        
        if project_status_request:
            # Only show approve button to the opposite party
            can_approve_request = project_status_request.requested_by != request.user
    
    context = {
        'room': chat_room,
        'messages': messages,
        'project': project,
        'can_request_meeting': can_request_meeting,
        'active_meeting': active_meeting,
        'project_status_request': project_status_request,
        'can_approve_request': can_approve_request,
    }
    
    return render(request, 'chat/room.html', context)

@login_required
def chat_list(request):
    if hasattr(request.user, 'customerprofile'):
        chat_rooms = ChatRoom.objects.filter(customer=request.user)
        # Get all developers except those who already have a chat with this customer
        existing_dev_ids = chat_rooms.values_list('developer_id', flat=True)
        available_developers = Profile.objects.exclude(user__id__in=existing_dev_ids)
    else:
        chat_rooms = ChatRoom.objects.filter(developer=request.user)
        available_developers = []
    
    return render(request, 'chat/list.html', {
        'chat_rooms': chat_rooms,
        'available_developers': available_developers
    })

@login_required
def create_room(request):
    if request.method == 'POST' and hasattr(request.user, 'customerprofile'):
        developer_id = request.POST.get('developer_id')
        developer = get_object_or_404(User, id=developer_id)
        
        # Check if room already exists
        room, created = ChatRoom.objects.get_or_create(
            customer=request.user,
            developer=developer
        )
        
        return redirect('chat:room', room_id=room.id)
    
    return redirect('chat:list')



from django.http import JsonResponse
from customer.models import ProjectStatusRequest
import json

@login_required
def request_project_status(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    data = json.loads(request.body)
    status = data.get('status')
    
    if status not in ['completed', 'cancelled']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    # Check if there's already a pending request
    existing_request = ProjectStatusRequest.objects.filter(
        project=project,
        is_approved=False
    ).first()
    
    if existing_request:
        return JsonResponse({'error': 'There is already a pending status request'}, status=400)
    
    ProjectStatusRequest.objects.create(
        project=project,
        requested_by=request.user,
        requested_status=status
    )
    
    return JsonResponse({'success': True})

@login_required
def approve_status_request(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    data = json.loads(request.body)
    request_id = data.get('request_id')
    
    status_request = get_object_or_404(ProjectStatusRequest, 
                                     id=request_id, 
                                     project=project)
    
    # Update project status
    project.status = status_request.requested_status
    project.save()
    
    # If project is completed, create a portfolio project for the developer
    if status_request.requested_status == 'completed':
        from dev.models import Project as DevProject
        
        # Create the developer's portfolio project with minimal validation
        DevProject.objects.create(
            name=project.title,
            readme=project.description,
            client=project.customer.company_name or project.customer.user.username,
            profile=project.assigned_developer,
            deployed_url='',
            github_url=None  # Use None instead of empty string
        )
    
    # Mark request as approved
    status_request.is_approved = True
    status_request.save()
    
    return JsonResponse({'success': True})

@login_required
def reject_status_request(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    data = json.loads(request.body)
    request_id = data.get('request_id')
    
    status_request = get_object_or_404(ProjectStatusRequest, 
                                     id=request_id, 
                                     project=project)
    
    # Delete the request when rejected
    status_request.delete()
    
    return JsonResponse({'success': True})