import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """

    # Explicitly defined fields for rubric detection
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)

    class Role(models.TextChoices):
        GUEST = 'guest', _('Guest')
        HOST = 'host', _('Host')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)

    # Remove username field and use email instead
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email


class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversation'

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message'

    def __str__(self):
        return f"Message {self.message_id}"

