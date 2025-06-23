from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import TimeoffRequest
from .serializer import TimeoffRequestSerializer
from department.models import UserProfile

class IsEmployeeOrManager(permissions.BasePermission):
    """
    Custom permission to allow:
    - Authenticated employees to create and view their own time-off requests.
    - Managers to view, approve, or reject time-off requests for their department.
    """
    def has_permission(self, request, view):
        # Allow authenticated users to access the view
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow users to view their own requests
        if obj.employee == request.user:
            return True
        
        # Allow managers to view/approve/reject requests for their department
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.is_manager and user_profile.department == obj.employee.userprofile.department:
                return True
        except UserProfile.DoesNotExist:
            pass
        
        return False

class TimeoffRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing TimeoffRequest instances.
    Supports listing, retrieving, creating, updating, and deleting time-off requests.
    Includes custom actions for approving and rejecting requests.
    """
    serializer_class = TimeoffRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeOrManager]

    def get_queryset(self):
        """
        Filter the queryset based on the user's role:
        - Employees see only their own requests.
        - Managers see requests from their department.
        """
        user = self.request.user
        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_manager:
                # Managers see all requests from their department
                return TimeoffRequest.objects.filter(
                    employee__userprofile__department=user_profile.department
                ).select_related('employee', 'requested_leave_type', 'reference_pay_period')
            else:
                # Employees see only their own requests
                return TimeoffRequest.objects.filter(
                    employee=user
                ).select_related('employee', 'requested_leave_type', 'reference_pay_period')
        except UserProfile.DoesNotExist:
            # If no UserProfile, restrict to user's own requests
            return TimeoffRequest.objects.filter(employee=user).select_related(
                'employee', 'requested_leave_type', 'reference_pay_period'
            )

    def perform_create(self, serializer):

        serializer.save(employee=self.request.user)

    def perform_update(self, serializer):
        """
        Restrict updates to non-final statuses and ensure only the owner or manager can update.
        """
        instance = serializer.instance
        if instance.status in ['approved', 'rejected']:
            raise PermissionDenied("Cannot update a request that has been approved or rejected.")
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsEmployeeOrManager])
    def approve(self, request, pk=None):
        """
        Custom action to approve a time-off request.
        Only managers can approve requests.
        """
        timeoff_request = self.get_object()
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if not user_profile.is_manager:
                raise PermissionDenied("Only managers can approve time-off requests.")
            if user_profile.department != timeoff_request.employee.userprofile.department:
                raise PermissionDenied("You can only approve requests for your department.")
            if timeoff_request.status != 'pending':
                raise PermissionDenied("Only pending requests can be approved.")
            
            timeoff_request.status = 'approved'
            timeoff_request.approved_by = request.user
            timeoff_request.approved_at = timezone.now()
            timeoff_request.save(process_timeoff_logic=False)  # Avoid re-splitting
            serializer = self.get_serializer(timeoff_request)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("User profile not found.")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsEmployeeOrManager])
    def reject(self, request, pk=None):
        """
        Custom action to reject a time-off request.
        Only managers can reject requests.
        """
        timeoff_request = self.get_object()
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if not user_profile.is_manager:
                raise PermissionDenied("Only managers can reject time-off requests.")
            if user_profile.department != timeoff_request.employee.userprofile.department:
                raise PermissionDenied("You can only reject requests for your department.")
            if timeoff_request.status != 'pending':
                raise PermissionDenied("Only pending requests can be rejected.")
            
            timeoff_request.status = 'rejected'
            timeoff_request.rejected_by = request.user
            timeoff_request.rejected_at = timezone.now()
            timeoff_request.save(process_timeoff_logic=False)  # Avoid re-splitting
            serializer = self.get_serializer(timeoff_request)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("User profile not found.")