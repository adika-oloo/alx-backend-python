from rest_framework import viewsets
from rest_framework.response import Response
from .models import Chat
from .serializers import ChatSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def list(self, request):
        # You can add custom logic here
        return super().list(request)
