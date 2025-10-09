from django.http import HttpResponseForbidden
from datetime import datetime
import time


class RestrictAccessByTimeMiddleware:
    """Middleware to restrict access outside 6PM–9PM."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour < 18 or current_hour >= 21:
            return HttpResponseForbidden("Access to the chat is restricted at this time.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """Middleware limiting users to 5 POST requests per minute per IP."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_log = {}

    def __call__(self, request):
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            now = time.time()
            if ip not in self.requests_log:
                self.requests_log[ip] = []
            self.requests_log[ip] = [ts for ts in self.requests_log[ip] if now - ts < 60]
            if len(self.requests_log[ip]) >= 5:
                return HttpResponseForbidden("Rate limit exceeded. Try again later.")
            self.requests_log[ip].append(now)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class RolePermissionMiddleware:
    """
    Middleware to restrict access to admin or moderator users only.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        # Ensure request has a user and is authenticated
        if not user or not user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this resource.")

        # Allow only users with role 'admin' or 'moderator'
        # (Assuming role stored as user.role or user.is_staff/superuser)
        user_role = getattr(user, "role", None)

        if user_role not in ["admin", "moderator"]:
            # Alternatively, if you use Django's default flags:
            if not (user.is_staff or user.is_superuser):
                return HttpResponseForbidden("You do not have permission to perform this action.")

        return self.get_response(request)
