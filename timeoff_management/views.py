from django.shortcuts import render
from rest_framework import viewsets
from department.models import Department
from department.serializer import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated
from payperiod.models import PayPeriod
from django.utils import timezone
from ptorequest.models import PTORequests
from timeoff_management.serializer import TimeOffManagementSerializer
from timeoff_management.filter import PTORequestFilter
from .pagination import TimeOffManagementPagination
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
class IsSuperuserCustom():
    """
    Custom permission class to check if the user is a superuser.
    This can be used to restrict access to certain views.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_superuser)
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser)

class DepartmentReturnView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for returning department information.
    This is a read-only viewset that allows users to retrieve department data.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsSuperuserCustom]

    def get_queryset(self):
        return super().get_queryset()
    

# This viewset can be used to return all the time off requests for the current pay period.
class TimeOffRequestViewCurrentPayPeriodAdmin(viewsets.ModelViewSet):
    """
    ViewSet for returning time off requests for the current pay period.
    This is a read-only viewset that allows users to retrieve time off request data.
    """
    permission_classes = [IsSuperuserCustom, IsAuthenticated]
    serializer_class = TimeOffManagementSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'trace']
    filterset_class = PTORequestFilter
    pagination_class = TimeOffManagementPagination  # Add this line for pagination

    def get_queryset(self):
        # Start with the base queryset
        queryset = PTORequests.objects.filter(status='pending')
        now = timezone.now()

        # You had a trailing comma and some extra commas in your original return statement.
        # Ensure your queryset is correctly ordered and returned.
        # Example: Filter by current pay period (you'll need to define how to calculate this)
        # For demonstration, let's assume 'start_date_time' should be within the last 30 days
        # You'll need to adjust this logic to truly represent "current pay period"
        # For example, you might have a 'pay_period_start' and 'pay_period_end' in your settings
        # or calculate it based on your company's pay cycle.

        # Example (replace with your actual pay period logic):
        # from datetime import timedelta
        # thirty_days_ago = now - timedelta(days=30)
        # queryset = queryset.filter(start_date_time__gte=thirty_days_ago)

        return queryset.order_by('start_date_time')

    # def perform_update(self, serializer):

    #     serializer.save()

class TimeOffTemplateView(TemplateView, LoginRequiredMixin):
    """
    Template view for the Time Off Management page.
    This view renders the template for the time off management interface.
    """
    template_name = 'manage_timeoff.html'
    login_url = 'login'  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

