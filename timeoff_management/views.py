from django.shortcuts import render
from rest_framework import viewsets
from department.models import Department
from department.serializer import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions

from django.utils import timezone
from ptorequest.models import PTORequests
from timeoff_management.serializer import TimeOffManagementSerializer
from timeoff_management.filter import PTORequestFilter
from .pagination import TimeOffManagementPagination
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import get_user_model # Import to get the User model
import logging
from notificationapp.models import Notification
from .services import send_pto_notification_and_email # Import the new service function
from department.models import UserProfile

logger = logging.getLogger(__name__)

# logger = logging.getLogger(__name__)
# Create your views here.
class IsSuperuserCustom(permissions.BasePermission):
    """
    Custom permission class to check if the user is a superuser.
    This can be used to restrict access to certain views.
    """
    def has_permission(self, request, view):
        return bool(request.user.is_superuser)
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_superuser)
    
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            user_profile = request.user.userprofile  # Assuming OneToOneField
            return user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False
        
class DepartmentReturnView(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for returning department information.
    This is a read-only viewset that allows users to retrieve department data.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsSuperuserCustom]
    permission_classes = [AllowAny]

    def get_queryset(self):
        return super().get_queryset()
    

# This viewset can be used to return all the time off requests for the current pay period.
class TimeOffRequestViewCurrentPayPeriodAdmin(viewsets.ModelViewSet):
    """
    ViewSet for returning time off requests for the current pay period.
    This is a read-only viewset that allows users to retrieve time off request data.
    """
    # permission_classes = [IsSuperuserCustom, IsAuthenticated , IsManager]
    serializer_class = TimeOffManagementSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'trace']
    filterset_class = PTORequestFilter
    pagination_class = TimeOffManagementPagination  # Add this line for pagination

    def get_queryset(self):
        # Start with the base queryset
        queryset = PTORequests.objects.filter(status='pending')
        now = timezone.now()

        return queryset.order_by('start_date_time')

    def perform_update(self, serializer):
        """
        Handles the update of an existing PTO request.
        """
        
        serializer.save()
        
        requester = self.request.user
        instance_status = serializer.instance.status
        
        # Call the service function to handle notifications and emails
        send_pto_notification_and_email(serializer.instance, requester, instance_status)
        


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
