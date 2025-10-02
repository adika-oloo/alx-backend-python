from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['receiver', 'timestamp']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.subject}"

class MessageLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Message Created'),
        ('read', 'Message Read'),
        ('status_changed', 'Status Changed'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} - {self.action}"

class UserMessageStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='message_stats')
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    unread_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats for {self.user.username}"
