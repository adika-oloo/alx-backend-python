import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        HOST = 'host', _('Host')
        ADMIN = 'admin', _('Admin')

    # Replace the default ID with UUID as primary key
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Override the default email field to make it unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False,
        db_index=True
    )
    
    # First name and last name are already in AbstractUser but we ensure they're not null
    first_name = models.CharField(_('first name'), max_length=150, blank=False, null=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=False)
    
    # Custom fields for our application
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
    
    # Password field is already in AbstractUser (stored as hash)
    # created_at is replaced by date_joined in AbstractUser
    
    # Use email as the unique identifier instead of username
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


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
    
    # Many-to-many relationship for participants
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text=_('Users participating in this conversation')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the conversation was created')
    )

    class Meta:
        db_table = 'conversation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        participant_count = self.participants.count()
        return f"Conversation {self.conversation_id} ({participant_count} participants)"


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
        related_name='sent_messages',
        help_text=_('User who sent the message')
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text=_('Conversation this message belongs to')
    )
    
    message_body = models.TextField(
        blank=False,
        null=False,
        help_text=_('Content of the message')
    )
    
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the message was sent')
    )

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
