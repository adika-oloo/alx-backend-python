import datetime
from django.http import HttpResponseForbidden
from django.utils.timezone import now

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Get current server time
        current_time = now()
        current_hour = current_time.hour
        
        # Define restricted hours (9 PM to 6 AM)
        # 21 = 9 PM, 6 = 6 AM
        is_restricted_time = current_hour >= 21 or current_hour < 6
        
        # Check if the request is for chat-related paths during restricted hours
        if is_restricted_time and self.is_chat_path(request.path):
            return HttpResponseForbidden(
                "Access to messaging services is restricted between 9 PM and 6 AM. "
                "Please try again during business hours."
            )
        
        # Process the request if not restricted
        response = self.get_response(request)
        return response
    
    def is_chat_path(self, path):
        """
        Check if the request path is related to chat/messaging functionality
        """
        chat_paths = [
            '/chats/',
            '/messages/',
            '/api/chats/',
            '/api/messages/',
            '/chat/',
            '/messaging/',
        ]
        
        # Check if the path starts with any of the chat-related paths
        return any(path.startswith(chat_path) for chat_path in chat_paths)

# Keep your existing logging middleware
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        timestamp = now()
        
        if request.user.is_authenticated:
            user = request.user.username
        else:
            user = 'AnonymousUser'
        
        log_entry = f"{timestamp} - User: {user} - Path: {request.path}\n"
        
        with open('requests.log', 'a') as f:
            f.write(log_entry)
        
        response = self.get_response(request)
        return response
