from django.test import TestCase
from django.contrib.auth.models import User
from .models import Chat

class ChatModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='test123')
        self.user2 = User.objects.create_user(username='user2', password='test123')

    def test_chat_creation(self):
        chat = Chat.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message="Hello, this is a test message"
        )
        self.assertEqual(str(chat), "user1 to user2: Hello, this is a test")
        self.assertFalse(chat.is_read)
