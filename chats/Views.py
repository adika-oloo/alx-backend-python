from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly

class MessageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
