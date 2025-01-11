from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from customer.models import CustomerProfile
from dev.models import Profile
from django.contrib.auth.models import User

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=chat_room)
    
    # Mark unread messages as read
    if request.user == chat_room.customer:
        messages.filter(sender=chat_room.developer, is_read=False).update(is_read=True)
    else:
        messages.filter(sender=chat_room.customer, is_read=False).update(is_read=True)
    
    return render(request, 'chat/room.html', {
        'room': chat_room,
        'messages': messages
    })

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
