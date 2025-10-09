import time
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseTooManyRequests
from datetime import datetime

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
    """
    Middleware that limits users to 5 messages (POST requests)
    per minute based on IP address.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store requests per IP: {ip: [timestamps]}
        self.requests_log = {}

    def __call__(self, request):
        # Only apply to POST requests (sending messages)
        if request.method == 'POST':
            ip = self.get_client_ip(request)
            now = time.time()

            # Initialize list for IP if not exists
            if ip not in self.requests_log:
                self.requests_log[ip] = []

            # Keep only timestamps within the last 60 seconds
            self.requests_log[ip] = [
                ts for ts in self.requests_log[ip] if now - ts < 60
            ]

            # Check if exceeds limit
            if len(self.requests_log[ip]) >= 5:
                return HttpResponseTooManyRequests("Rate limit exceeded: Try again later.")

            # Record new message timestamp
            self.requests_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Helper to extract client IP."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip




