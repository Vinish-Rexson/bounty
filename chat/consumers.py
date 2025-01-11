import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatMessage, ChatRoom
from customer.models import MeetingRequest
from django.urls import reverse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = text_data_json['message']
            # Save the message
            await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': self.scope['user'].id,
                    'timestamp': timezone.now().isoformat()
                }
            )
        elif message_type == 'meeting_request':
            # Create meeting request
            meeting_id = await self.create_meeting_request()
            
            # Send meeting request to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'meeting_request',
                    'meeting_id': meeting_id,
                    'sender_id': self.scope['user'].id
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

    async def meeting_request(self, event):
        # Send meeting request to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meeting_request',
            'meeting_id': event['meeting_id'],
            'sender_id': event['sender_id']
        }))

    async def meeting_accepted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'meeting_accepted',
            'meeting_id': event['meeting_id'],
            'room_id': event['room_id'],
            'join_url': reverse('dev:join_meeting', kwargs={'meeting_id': event['meeting_id']})
        }))

    async def meeting_declined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'meeting_declined',
            'meeting_id': event['meeting_id']
        }))

    @database_sync_to_async
    def save_message(self, message):
        ChatMessage.objects.create(
            room_id=self.room_id,
            sender=self.scope['user'],
            content=message
        )

    @database_sync_to_async
    def create_meeting_request(self):
        from customer.models import MeetingRequest
        import uuid
        
        # Get the chat room
        chat_room = ChatRoom.objects.get(id=self.room_id)
        
        # Determine customer and developer based on sender
        if hasattr(self.scope['user'], 'customerprofile'):
            customer = self.scope['user'].customerprofile
            developer = chat_room.developer.profile
        else:
            customer = chat_room.customer.customerprofile
            developer = self.scope['user'].profile
        
        # Create the meeting request
        meeting = MeetingRequest.objects.create(
            customer=customer,
            developer=developer,
            room_id=str(uuid.uuid4()),
            status='pending'
        )
        return meeting.id
