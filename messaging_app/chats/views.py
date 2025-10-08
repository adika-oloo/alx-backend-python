from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Message, Conversation
from .serializers import MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")
        return Message.objects.filter(conversation__id=conversation_id).order_by('-created_at')

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get("conversation_id")
        conversation = Conversation.objects.get(id=conversation_id)

        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant of this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(sender=self.request.user, conversation=conversation)

