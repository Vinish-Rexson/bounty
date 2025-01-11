from django.db import models
from django.contrib.auth.models import User
from customer.models import Project

class ChatRoom(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, related_name='customer_chats', on_delete=models.CASCADE)
    developer = models.ForeignKey(User, related_name='developer_chats', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='chat_rooms', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'developer', 'project']

    def __str__(self):
        return f'Chat: {self.project.title} ({self.customer.username} - {self.developer.username})'

class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender.username}: {self.content[:50]}'
