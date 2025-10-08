import logging
from datetime import datetime, time
from django.http import JsonResponse

# Logger for request logs
logger = logging.getLogger('request_logger')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access outside of allowed hours (e.g., 8 AM - 6 PM)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Define working hours (you can customize this)
        self.start_time = time(8, 0, 0)   # 8:00 AM
        self.end_time = time(18, 0, 0)    # 6:00 PM

    def __call__(self, request):
        current_time = datetime.now().time()
        if not (self.start_time <= current_time <= self.end_time):
            return JsonResponse(
                {"detail": "Access restricted. Please try again during working hours (8 AM - 6 PM)."},
                status=403
            )
        return self.get_response(request)
