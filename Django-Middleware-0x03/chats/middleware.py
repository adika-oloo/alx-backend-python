import os
from datetime import datetime
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to write to a file"""
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Configure file handler
        log_file = os.path.join(logs_dir, 'requests.log')
        
        # Create a specific logger for requests
        self.request_logger = logging.getLogger('request_logger')
        self.request_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        if self.request_logger.handlers:
            self.request_logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.request_logger.addHandler(file_handler)
        
        # Prevent propagation to parent loggers
        self.request_logger.propagate = False

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called
        response = self.get_response(request)
        
        # Code to be executed for each request/response after the view is called
        self.log_request(request)
        
        return response

    def log_request(self, request):
        """Log the request details"""
        # Get user information
        user = self.get_user_info(request)
        
        # Log the request
        log_message = f"User: {user} - Path: {request.path} - Method: {request.method}"
        
        # Log to file
        self.request_logger.info(log_message)
        
        # Also log to console for development
        print(f"{datetime.now()} - {log_message}")

    def get_user_info(self, request):
        """Extract user information from request"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"{request.user.username} (ID: {request.user.id})"
        else:
            return "AnonymousUser"
