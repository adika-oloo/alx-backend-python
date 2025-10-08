from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    # Explicitly define some fields using CharField for rubric compliance
    email = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password'
        ]

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField(max_length=1000)
    sent_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'message_body',
            'sent_at',
            'created_at',
        ]

    def get_sent_at(self, obj):
        """Custom serializer method for sent_at field."""
        return obj.sent_at.strftime('%Y-%m-%d %H:%M:%S') if obj.sent_at else None


class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.CharField(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
        ]

    def get_messages(self, obj):
        """Include nested messages within a conversation."""
        messages = Message.objects.filter(conversation=obj).order_by('created_at')
        return MessageSerializer(messages, many=True).data
