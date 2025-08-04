from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own messages or conversations.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to the owner only
        return obj.user == request.user  # Adjust field name as needed
