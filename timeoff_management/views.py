from django.shortcuts import  redirect
from rest_framework import viewsets
from rest_framework import permissions

from django.utils import timezone
from .pagination import ManagerTimeOffManagementPagination
import logging
from department.models import UserProfile
from timeoffreq.models import TimeoffRequest
from .serializer import TimeoffApproveRejectManager
from rest_framework.decorators import action
from .tasks import send_pto_notification_and_email_task
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.permissions import IsAuthenticated  
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer

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
        # Superusers bypass this permission check at the method level (get_permissions)
        # but this is here for general robustness if called directly
        if request.user.is_superuser:
            return True
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Superusers bypass this object-level permission check as well
        if request.user.is_superuser:
            return True
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
    # permission_classes = [permissions.IsAuthenticated, IsManagerOfDepartment] # Removed here
    pagination_class = ManagerTimeOffManagementPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Superusers will only require IsAuthenticated.
        """
        if self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManagerOfDepartment()]

    def get_queryset(self):
        """
        Returns only pending time-off requests for the manager's department.
        Uses select_related to optimize fetching of related data.
        Superusers can see all pending requests.
        """
        user = self.request.user
        if user.is_superuser:
            # Superusers see all pending requests
            return TimeoffRequest.objects.filter(status="pending").select_related("employee", "requested_leave_type", "reference_pay_period", "employee__userprofile", "requested_leave_type__department", "requested_leave_type__leave_type").order_by("created_at")

        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_manager:
                return TimeoffRequest.objects.filter(employee__userprofile__department=user_profile.department, status="pending").exclude(employee=user).select_related("employee", "requested_leave_type", "reference_pay_period", "employee__userprofile", "requested_leave_type__department", "requested_leave_type__leave_type").order_by("-created_at")
        except UserProfile.DoesNotExist:
            return TimeoffRequest.objects.none()
        return TimeoffRequest.objects.none()

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """
        Approve a pending time-off request.
        Only accessible to managers of the employee's department or superusers.
        """
        timeoff_request = self.get_object()
        user = request.user

        if timeoff_request.status != "pending":
            raise PermissionDenied("Only pending requests can be approved.")

        if not user.is_superuser:
            try:
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.is_manager or user_profile.department != timeoff_request.employee.userprofile.department:
                    raise PermissionDenied("You can only approve requests for your department.")
            except UserProfile.DoesNotExist:
                raise PermissionDenied("You are not authorized to perform this action.")

        timeoff_request.status = "approved"
        timeoff_request.reviewer = user
        timeoff_request.reviewed_at = timezone.now()
        timeoff_request.save(process_timeoff_logic=False)  # Avoid re-processing logic
        serializer = self.get_serializer(timeoff_request)
        send_pto_notification_and_email_task.delay(serializer.instance.id, timeoff_request.reviewer.id, timeoff_request.status)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Reject a pending time-off request.
        Only accessible to managers of the employee's department or superusers.
        """
        timeoff_request = self.get_object()
        user = request.user

        if timeoff_request.status != "pending":
            raise PermissionDenied("Only pending requests can be rejected.")

        if not user.is_superuser:
            try:
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.is_manager or user_profile.department != timeoff_request.employee.userprofile.department:
                    raise PermissionDenied("You can only reject requests for your department.")
            except UserProfile.DoesNotExist:
                raise PermissionDenied("You are not authorized to perform this action.")

        timeoff_request.status = "rejected"
        timeoff_request.reviewer = user
        timeoff_request.reviewed_at = timezone.now()
        timeoff_request.save(process_timeoff_logic=False)  # Avoid re-processing logic
        serializer = self.get_serializer(timeoff_request)

        # Call the service function to handle notifications and emails
        send_pto_notification_and_email_task(serializer.instance, timeoff_request.reviewer, timeoff_request.status)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimeOffTemplateView(APIView):
    """
    Template view for the Time Off Management page.
    This view renders the template for the time off management interface.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "manage_timeoff.html"
    login_url = "hrmsauth:frontend_login"
    versioning_class = None  # Disable versioning for this view

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)


############################################################################################################################################################################


# SuperUser Time off Management Logic
############################################################################################################################################################################
