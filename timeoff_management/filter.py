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
    

    # Filter by leave_type (assuming leave_type_display is a ForeignKey to LeaveType model)
    leave_type_display = filters.CharFilter(field_name='leave_type__name', lookup_expr='icontains')

    # You could also add date range filters if needed
    # start_date__gte = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    # end_date__lte = filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = PTORequests
        fields = [
            'department_name_display',
            'status',
            'leave_type_display',
        ]
