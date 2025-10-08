from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow users to view/edit their own data.
    """

    def has_object_permission(self, request, view, obj):
        # For messages: check if sender is the user
        if hasattr(obj, 'sender'):
            return obj.sender == request.user

        # For conversations: check if user is among participants
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        # Fallback for user object
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
