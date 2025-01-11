from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, ChatMessage
from customer.models import CustomerProfile, Project, MeetingRequest
from dev.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

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
    
    context = {
        'room': chat_room,
        'messages': messages,
        'project': project,
        'can_request_meeting': can_request_meeting,
        'active_meeting': active_meeting
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
