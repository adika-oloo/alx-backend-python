from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Message, MessageLog, UserMessageStats
from .signals import update_user_message_stats

class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user('sender', 'sender@test.com', 'password')
        self.receiver = User.objects.create_user('receiver', 'receiver@test.com', 'password')

    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Subject',
            body='Test Body'
        )
        
        self.assertEqual(message.subject, 'Test Subject')
        self.assertEqual(message.status, 'sent')
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.timestamp)

    def test_message_str_representation(self):
        """Test string representation of message"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Subject',
            body='Test Body'
        )
        
        expected_str = f"{self.sender.username} to {self.receiver.username}: Test Subject"
        self.assertEqual(str(message), expected_str)

class MessageSignalsTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user('sender', 'sender@test.com', 'password')
        self.receiver = User.objects.create_user('receiver', 'receiver@test.com', 'password')

    def test_message_creation_signal(self):
        """Test that signals are triggered when message is created"""
        # Check initial state
        self.assertEqual(MessageLog.objects.count(), 0)
        
        # Create message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Signal',
            body='Test Body'
        )
        
        # Check that log was created
        self.assertEqual(MessageLog.objects.count(), 1)
        log = MessageLog.objects.first()
        self.assertEqual(log.action, 'created')
        self.assertEqual(log.message, message)

    def test_user_stats_creation_on_message(self):
        """Test that user stats are updated when message is created"""
        # Create message
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Stats',
            body='Test Body'
        )
        
        # Check sender stats
        sender_stats = UserMessageStats.objects.get(user=self.sender)
        self.assertEqual(sender_stats.messages_sent, 1)
        
        # Check receiver stats
        receiver_stats = UserMessageStats.objects.get(user=self.receiver)
        self.assertEqual(receiver_stats.messages_received, 1)
        self.assertEqual(receiver_stats.unread_count, 1)

    def test_message_status_change_signal(self):
        """Test signals when message status changes"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Status Change',
            body='Test Body'
        )
        
        # Clear initial logs
        MessageLog.objects.all().delete()
        
        # Change status to read
        message.status = 'read'
        message.save()
        
        # Check that status change was logged
        self.assertEqual(MessageLog.objects.count(), 1)
        log = MessageLog.objects.first()
        self.assertEqual(log.action, 'status_changed')
        
        # Check that message was marked as read
        message.refresh_from_db()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

    def test_unread_count_update(self):
        """Test that unread count decreases when message is read"""
        # Create multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                subject=f'Test Message {i}',
                body='Test Body'
            )
        
        receiver_stats = UserMessageStats.objects.get(user=self.receiver)
        self.assertEqual(receiver_stats.unread_count, 3)
        
        # Mark one message as read
        message = Message.objects.first()
        message.status = 'read'
        message.save()
        
        # Check that unread count decreased
        receiver_stats.refresh_from_db()
        self.assertEqual(receiver_stats.unread_count, 2)

class MessageLogTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user('sender', 'sender@test.com', 'password')
        self.receiver = User.objects.create_user('receiver', 'receiver@test.com', 'password')

    def test_message_log_creation(self):
        """Test MessageLog model"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Test Log',
            body='Test Body'
        )
        
        log = MessageLog.objects.create(
            message=message,
            action='created',
            details={'test': 'data'}
        )
        
        self.assertEqual(log.message, message)
        self.assertEqual(log.action, 'created')
        self.assertEqual(log.details, {'test': 'data'})

class UserMessageStatsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')

    def test_user_stats_creation(self):
        """Test UserMessageStats model and auto-creation"""
        # Stats should be auto-created via signal
        stats = UserMessageStats.objects.get(user=self.user)
        
        self.assertEqual(stats.messages_sent, 0)
        self.assertEqual(stats.messages_received, 0)
        self.assertEqual(stats.unread_count, 0)

    def test_update_user_message_stats_helper(self):
        """Test the update_user_message_stats helper function"""
        stats = UserMessageStats.objects.get(user=self.user)
        
        # Test sent update
        update_user_message_stats(self.user, 'sent')
        stats.refresh_from_db()
        self.assertEqual(stats.messages_sent, 1)
        
        # Test received update
        update_user_message_stats(self.user, 'received')
        stats.refresh_from_db()
        self.assertEqual(stats.messages_received, 1)
        self.assertEqual(stats.unread_count, 1)

class IntegrationTest(TestCase):
    """Integration tests for the complete messaging flow"""
    
    def setUp(self):
        self.sender = User.objects.create_user('sender', 'sender@test.com', 'password')
        self.receiver = User.objects.create_user('receiver', 'receiver@test.com', 'password')

    def test_complete_message_flow(self):
        """Test complete message flow with all signals"""
        # Initial state
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(MessageLog.objects.count(), 0)
        
        # Create message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject='Integration Test',
            body='Test Body'
        )
        
        # Verify message creation
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageLog.objects.filter(action='created').count(), 1)
        
        # Verify user stats
        sender_stats = UserMessageStats.objects.get(user=self.sender)
        receiver_stats = UserMessageStats.objects.get(user=self.receiver)
        self.assertEqual(sender_stats.messages_sent, 1)
        self.assertEqual(receiver_stats.messages_received, 1)
        self.assertEqual(receiver_stats.unread_count, 1)
        
        # Mark as read
        message.status = 'read'
        message.save()
        
        # Verify read status and logs
        message.refresh_from_db()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
        self.assertEqual(MessageLog.objects.filter(action='status_changed').count(), 1)
        
        # Verify unread count updated
        receiver_stats.refresh_from_db()
        self.assertEqual(receiver_stats.unread_count, 0)
