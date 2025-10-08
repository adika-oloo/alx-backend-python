import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        HOST = 'host', _('Host')
        ADMIN = 'admin', _('Admin')

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    first_name = models.CharField(_('first name'), max_length=150, blank=False, null=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=False)
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False,
        db_index=True
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('User phone number')
    )
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        blank=False,
        null=False
    )
    
    password = models.CharField(_('password'), max_length=128)
    
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Conversation model to track which users are involved in a conversation
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text=_('Users participating in this conversation')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Message model containing sender, conversation and message content
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_body = models.TextField(blank=False, null=False)
    
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['sent_at']),
            models.Index(fields=['sender', 'sent_at']),
            models.Index(fields=['conversation', 'sent_at']),
        ]

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
