class RolepermissionMiddleware:
    """
    Middleware to restrict access to admin or moderator users only.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        # Check authentication
        if not user or not user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this resource.")

        # Check role (assuming stored as user.role)
        user_role = getattr(user, "role", None)

        # Allow only admin or moderator
        if user_role not in ["admin", "moderator"]:
            # Fallback: Django default permissions
            if not (user.is_staff or user.is_superuser):
                return HttpResponseForbidden("You do not have permission to perform this action.")

        return self.get_response(request)

