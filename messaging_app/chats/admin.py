from django.contrib import admin
from .models import Chat

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'message', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['message', 'sender__username', 'receiver__username']
