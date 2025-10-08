from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access its messages or details.
    """

    def has_permission(self, request, view):
        # Ensure user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If the object is a conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        # If the object is a message, check its conversation participants
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
            if request.user not in conversation.participants.all():
                return False

            # Restrict write operations (PUT, PATCH, DELETE) to participants only
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return request.user in conversation.participants.all()

        return True

