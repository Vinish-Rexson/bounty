from django.contrib import admin
from .models import ChatRoom, ChatMessage

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'developer', 'project', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__username', 'developer__username', 'project__title')
    date_hierarchy = 'created_at'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'content', 'timestamp')
    list_filter = ('timestamp', 'sender')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
