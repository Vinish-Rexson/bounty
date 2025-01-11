from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    customer = models.ForeignKey(User, related_name='customer_chats', on_delete=models.CASCADE)
    developer = models.ForeignKey(User, related_name='developer_chats', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'developer']

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
