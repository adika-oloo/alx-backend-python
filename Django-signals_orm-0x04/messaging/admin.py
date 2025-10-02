from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Message, MessageLog, UserMessageStats

class MessageLogInline(admin.TabularInline):
    model = MessageLog
    extra = 0
    readonly_fields = ['action', 'details', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'receiver', 'status', 'timestamp', 'is_read']
    list_filter = ['status', 'is_read', 'timestamp']
    search_fields = ['subject', 'body', 'sender__username', 'receiver__username']
    readonly_fields = ['timestamp', 'read_at']
    inlines = [MessageLogInline]
    
    fieldsets = (
        ('Message Information', {
            'fields': ('sender', 'receiver', 'subject', 'body')
        }),
        ('Status Information', {
            'fields': ('status', 'is_read', 'timestamp', 'read_at')
        }),
    )

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['message', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['message__subject', 'message__sender__username']
    readonly_fields = ['message', 'action', 'details', 'created_at']
    
    def has_add_permission(self, request):
        return False

@admin.register(UserMessageStats)
class UserMessageStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'messages_sent', 'messages_received', 'unread_count', 'last_activity']
    list_filter = ['last_activity']
    search_fields = ['user__username']
    readonly_fields = ['last_activity']

class UserMessageStatsInline(admin.StackedInline):
    model = UserMessageStats
    can_delete = False
    verbose_name_plural = 'Message Statistics'
    readonly_fields = ['messages_sent', 'messages_received', 'unread_count', 'last_activity']

class UserAdmin(BaseUserAdmin):
    inlines = [UserMessageStatsInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
