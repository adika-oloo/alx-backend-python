from datetime import datetime
from django.http import HttpResponseForbidden


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the chat app
    between 6 AM and 9 PM. Outside these hours, it
    returns a 403 Forbidden response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current server hour (0–23)
        current_hour = datetime.now().hour

        # Allow only between 6 AM (06) and 9 PM (21)
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the chat is restricted between 9 PM and 6 AM."
            )

        # Otherwise continue request
        return self.get_response(request)

