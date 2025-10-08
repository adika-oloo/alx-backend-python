from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()

        # Allow send (POST), update (PUT/PATCH), and delete (DELETE)
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return request.user in obj.conversation.participants.all()

        return False
