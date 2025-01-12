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
        message_type = text_data_json.get('type')

        if message_type == 'meeting_stats':
            # Broadcast meeting stats to all connected clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'meeting_stats',
                    'meeting_id': text_data_json.get('meeting_id'),
                    'duration': text_data_json.get('duration'),
                    'participant_count': text_data_json.get('participant_count'),
                    'screen_shares': text_data_json.get('screen_shares'),
                    'mic_toggles': text_data_json.get('mic_toggles'),
                    'camera_toggles': text_data_json.get('camera_toggles'),
                    'is_final': text_data_json.get('is_final')
                }
            )
        else:
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
            elif message_type == 'meeting_response':
                # Handle meeting response
                meeting_id = text_data_json['meeting_id']
                action = text_data_json['action']
                
                if action == 'accept':
                    # Update meeting request and get room ID
                    room_id = await self.accept_meeting_request(meeting_id)
                    
                    # Send acceptance to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'meeting_accepted',
                            'meeting_id': meeting_id,
                            'room_id': room_id
                        }
                    )
                elif action == 'reject':
                    # Update meeting request
                    await self.decline_meeting_request(meeting_id)
                    
                    # Send rejection to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'meeting_declined',
                            'meeting_id': meeting_id
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

    async def meeting_stats(self, event):
        # Send meeting stats to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meeting_stats',
            'meeting_id': event['meeting_id'],
            'duration': event['duration'],
            'participant_count': event['participant_count'],
            'screen_shares': event['screen_shares'],
            'mic_toggles': event['mic_toggles'],
            'camera_toggles': event['camera_toggles'],
            'is_final': event['is_final']
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

    @database_sync_to_async
    def accept_meeting_request(self, meeting_id):
        meeting = MeetingRequest.objects.get(id=meeting_id)
        meeting.status = 'accepted'
        meeting.save()
        return meeting.room_id

    @database_sync_to_async
    def decline_meeting_request(self, meeting_id):
        meeting = MeetingRequest.objects.get(id=meeting_id)
        meeting.status = 'declined'
        meeting.save()

class MeetingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.room_group_name = f'meeting_{self.meeting_id}'

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
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'meeting_message')
            
            print(f"Received WebSocket message: {message_type}")  # Debug log
            
            # Create a base event with common fields
            event = {
                'type': message_type,
                'meeting_id': self.meeting_id,
                'user_name': data.get('user_name', 'Anonymous'),
            }
            
            # Add additional fields based on message type
            if message_type == 'meeting_ended':
                print(f"Processing meeting_ended request from {data.get('ended_by')}")  # Debug log
                event.update({
                    'ended_by': data.get('ended_by', 'anonymous'),
                    'user_name': data.get('user_name', 'Anonymous'),
                    'redirect_url': data.get('redirect_url', '/')
                })
            elif message_type == 'meeting_end_confirmed':
                event.update({
                    'confirmed_by': data.get('confirmed_by', 'anonymous'),
                    'user_name': data.get('user_name', 'Anonymous')
                })
            elif message_type == 'meeting_end_rejected':
                event.update({
                    'rejected_by': data.get('rejected_by', 'anonymous'),
                    'user_name': data.get('user_name', 'Anonymous')
                })
            
            print(f"Broadcasting event to group: {event}")  # Debug log
            
            # Broadcast to all clients in the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                event
            )
        except Exception as e:
            print(f"Error in receive: {str(e)}")  # Debug log
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def meeting_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def meeting_ended(self, event):
        print(f"Sending meeting_ended event to client: {event}")  # Debug log
        # Send meeting ended notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meeting_ended',
            'meeting_id': str(event['meeting_id']),
            'ended_by': event.get('ended_by', 'anonymous'),
            'user_name': event.get('user_name', 'Anonymous'),
            'redirect_url': event.get('redirect_url', '/')
        }))

    async def meeting_end_confirmed(self, event):
        # Send confirmation to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meeting_end_confirmed',
            'meeting_id': str(event['meeting_id']),
            'confirmed_by': event.get('confirmed_by', 'anonymous'),
            'user_name': event.get('user_name', 'Anonymous')
        }))

    async def meeting_end_rejected(self, event):
        # Send rejection to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meeting_end_rejected',
            'meeting_id': str(event['meeting_id']),
            'rejected_by': event.get('rejected_by', 'anonymous'),
            'user_name': event.get('user_name', 'Anonymous')
        }))
