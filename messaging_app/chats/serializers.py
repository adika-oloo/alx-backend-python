from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role'
        ]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model
    Includes sender info and timestamps
    """
    sender = UserSerializer(read_only=True)  # Nested sender details

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body',
            'sent_at',
            'created_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model
    Includes nested participants and messages
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

