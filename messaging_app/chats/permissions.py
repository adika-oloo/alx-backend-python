from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only:
    - Authenticated users
    - Users who are participants in the conversation
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For message objects (which have a conversation)
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()

        # For conversation objects directly
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        return False
