# time_off/filters.py
import django_filters
from django_filters import rest_framework as filters
from django.utils import timezone
from ptorequest.models import PTORequests
from payperiod.models import PayPeriod

class PTORequestFilter(filters.FilterSet):
   

    # Filter by department name (case-insensitive contains)
    department_name_display = filters.CharFilter(field_name='department_name__name', lookup_expr='icontains')

    # Filter by status (e.g., approved, pending, rejected)
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')

    # Filter by leave_type (assuming leave_type_display is a ForeignKey to LeaveType model)
    leave_type_display = filters.CharFilter(field_name='leave_type_display__name', lookup_expr='icontains')

    # You could also add date range filters if needed
    # start_date__gte = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    # end_date__lte = filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = PTORequests
        fields = [
            'department_name_display',
            'status',
            'leave_type_display',
            # Add other fields you want to enable direct filtering for
            # 'user', # If you want to filter by user ID
            # 'created_at',
        ]

    # You might still need to handle the current pay period logic here if it's not a direct filterable field
    # def __init__(self, *args, **kwargs):
    #     queryset = PTORequests.objects.filter(status='pending')
    #     now = timezone.now() 
    #     return queryset.order_by('-created_at')