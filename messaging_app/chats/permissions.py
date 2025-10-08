from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Allows access only to authenticated users.
    - Restricts actions to participants of a conversation.
    """

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission:
        Allow access only if the user is a participant of the conversation.
        """
        # If the object is a Message, check if the user participates in its conversation
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
        else:
            conversation = obj

        if request.user in conversation.participants.all():
            return True

        # Deny access explicitly if user not a participant
        raise PermissionDenied("You are not a participant in this conversation.")

