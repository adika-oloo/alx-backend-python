from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'is_read']
        read_only_fields = ['timestamp']
