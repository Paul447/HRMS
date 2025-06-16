from rest_framework.pagination import PageNumberPagination

class TimeOffManagementPagination(PageNumberPagination):
    """
    Custom pagination class for Time Off Management views.
    This class can be used to control the number of results returned per page.
    """
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set the page size
    max_page_size = 100  # Maximum number of items per page