from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

from django.utils import timezone
from .pagination import ManagerTimeOffManagementPagination
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from department.models import UserProfile
from timeoffreq.models import TimeoffRequest
from .serializer import TimeoffApproveRejectManager
from rest_framework.decorators import action

logger = logging.getLogger(__name__)

                                         # Manager Time off Management Logic
############################################################################################################################################################################
class IsManagerOfDepartment(permissions.BasePermission):
    """
    Custom permission to allow only managers of the specific department to access requests.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.is_manager and user_profile.department == obj.employee.userprofile.department
        except UserProfile.DoesNotExist:
            return False

class ManagerTimeoffApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managers to list pending time-off requests in their department
    and perform approve or reject actions.
    """
    serializer_class = TimeoffApproveRejectManager
    permission_classes = [permissions.IsAuthenticated, IsManagerOfDepartment]
    pagination_class = ManagerTimeOffManagementPagination 
    
    def get_queryset(self):
        """
        Returns only pending time-off requests for the manager's department.
        Uses select_related to optimize fetching of related data.
        """
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_manager:
                return TimeoffRequest.objects.filter(
                    employee__userprofile__department=user_profile.department,
                    status='pending'
                ).exclude(employee=user).select_related(
                    'employee', 'requested_leave_type', 'reference_pay_period',
                    'employee__userprofile', 'requested_leave_type__department',
                    'requested_leave_type__leave_type'
                ).order_by('-created_at')
        except UserProfile.DoesNotExist:
            return TimeoffRequest.objects.none()
        return TimeoffRequest.objects.none()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a pending time-off request.
        Only accessible to managers of the employee's department.
        """
        timeoff_request = self.get_object()
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.department != timeoff_request.employee.userprofile.department:
            raise PermissionDenied("You can only approve requests for your department.")
        if timeoff_request.status != 'pending':
            raise PermissionDenied("Only pending requests can be approved.")

        timeoff_request.status = 'approved'
        timeoff_request.reviewer = request.user
        timeoff_request.reviewed_at = timezone.now()
        timeoff_request.save(process_timeoff_logic=False)  # Avoid re-processing logic
        serializer = self.get_serializer(timeoff_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a pending time-off request.
        Only accessible to managers of the employee's department.
        """
        timeoff_request = self.get_object()
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.department != timeoff_request.employee.userprofile.department:
            raise PermissionDenied("You can only reject requests for your department.")
        if timeoff_request.status != 'pending':
            raise PermissionDenied("Only pending requests can be rejected.")

        timeoff_request.status = 'rejected'
        timeoff_request.reviewer = request.user
        timeoff_request.reviewed_at = timezone.now()
        timeoff_request.save(process_timeoff_logic=False)  # Avoid re-processing logic
        serializer = self.get_serializer(timeoff_request)
        return Response(serializer.data)
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
                                         # Manager Time off Management Logic
############################################################################################################################################################################


                                         # SuperUser Time off Management Logic
############################################################################################################################################################################
