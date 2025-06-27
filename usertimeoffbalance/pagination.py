from rest_framework.pagination import PageNumberPagination


class TimeoffBalancePagination(PageNumberPagination):
    """
    Custom pagination class for Timeoff Balance API.
    """

    page_size = 10  # Default number of items per page
    page_size_query_param = "page_size"  # Allow clients to set the page size
    max_page_size = 100  # Maximum allowed page size to prevent abuse
    last_page_strings = ("last",)  # Optional: allows clients to request the last page with 'last'
