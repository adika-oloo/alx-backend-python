import logging
from datetime import datetime, time
from django.http import JsonResponse

# Logger for request logs
logger = logging.getLogger('request_logger')


class RequestLoggingMiddleware:
    """
    Middleware to log each request with timestamp, user, and path.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        with open("requests.log", "a") as f:
            f.write(log_message + "\n")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access outside allowed hours (8 AM - 6 PM)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.start_time = time(8, 0, 0)
        self.end_time = time(18, 0, 0)

    def __call__(self, request):
        current_time = datetime.now().time()
        if not (self.start_time <= current_time <= self.end_time):
            return JsonResponse(
                {"detail": "Access restricted. Please try again during working hours (8 AM - 6 PM)."},
                status=403
            )
        return self.get_response(request)

