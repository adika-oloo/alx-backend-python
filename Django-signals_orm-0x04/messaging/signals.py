from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import Message, MessageLog, UserMessageStats

@receiver(post_save, sender=Message)
def log_message_creation(sender, instance, created, **kwargs):
    """
    Signal to log message creation and update user statistics
    """
    if created:
        # Log the message creation
        MessageLog.objects.create(
            message=instance,
            action='created',
            details={
                'sender': instance.sender.username,
                'receiver': instance.receiver.username,
                'subject': instance.subject
            }
        )

        # Update user statistics
        update_user_message_stats(instance.sender, 'sent')
        update_user_message_stats(instance.receiver, 'received')

@receiver(pre_save, sender=Message)
def handle_message_status_change(sender, instance, **kwargs):
    """
    Signal to handle message status changes and mark as read
    """
    if instance.pk:
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            
            # Check if status changed to 'read'
            if old_instance.status != 'read' and instance.status == 'read':
                instance.is_read = True
                instance.read_at = timezone.now()
                
                # Log the read action
                MessageLog.objects.create(
                    message=instance,
                    action='read',
                    details={'read_at': instance.read_at.isoformat()}
                )
                
                # Update unread count for receiver
                update_user_message_stats(instance.receiver, 'read_update')

            # Log status changes
            elif old_instance.status != instance.status:
                MessageLog.objects.create(
                    message=instance,
                    action='status_changed',
                    details={
                        'from_status': old_instance.status,
                        'to_status': instance.status
                    }
                )
                
        except Message.DoesNotExist:
            pass

@receiver(post_save, sender=Message)
def update_unread_count(sender, instance, **kwargs):
    """
    Signal to update unread message count for users
    """
    if instance.is_read:
        # Decrement unread count for receiver
        stats, created = UserMessageStats.objects.get_or_create(user=instance.receiver)
        if stats.unread_count > 0:
            stats.unread_count -= 1
            stats.save()

def update_user_message_stats(user, action):
    """
    Helper function to update user message statistics
    """
    stats, created = UserMessageStats.objects.get_or_create(user=user)
    
    if action == 'sent':
        stats.messages_sent += 1
    elif action == 'received':
        stats.messages_received += 1
        stats.unread_count += 1
    elif action == 'read_update':
        # Recalculate unread count
        stats.unread_count = Message.objects.filter(
            receiver=user, 
            is_read=False
        ).count()
    
    stats.save()

# Signal to initialize user stats when a new user is created
@receiver(post_save, sender='auth.User')
def create_user_message_stats(sender, instance, created, **kwargs):
    """
    Create UserMessageStats when a new User is created
    """
    if created:
        UserMessageStats.objects.create(user=instance)
