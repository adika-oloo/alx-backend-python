from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Displays 20 messages per page by default.
    """
    page_size = 20
    page_size_query_param = 'page_size'  # Optional: allow ?page_size=10
    max_page_size = 100
