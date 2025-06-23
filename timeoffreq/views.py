from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import TimeoffRequest
from .serializer import TimeoffRequestSerializer , TimeoffRequestSerializerEmployee
from department.models import UserProfile
from payperiod.models import PayPeriod  # Add this import for PayPeriod
from rest_framework.exceptions import ValidationError

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
        
        # Allow the user to view time-off requests if they have permission of th
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
    serializer_class = TimeoffRequestSerializerEmployee
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
        

class IsEmployeeWithTimeoffPermission(permissions.BasePermission):
    """
    Custom permission to allow a user to manipulate a time-off request
    ONLY IF they are the employee associated with the request
    AND they possess the 'is_time_off' permission.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_owner = (obj.employee == request.user)
        has_timeoff_permission = False
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            has_timeoff_permission = user_profile.is_time_off
        except UserProfile.DoesNotExist:
            has_timeoff_permission = False
        return is_owner and has_timeoff_permission

class TimeoffRequestViewSetEmployee(viewsets.ModelViewSet):
    """
    ViewSet for managing TimeoffRequest instances for employees.
    Supports listing, retrieving, creating, updating, and deleting time-off requests.
    Restricted to employee-owned requests with 'is_time_off' permission.
    """
    serializer_class = TimeoffRequestSerializerEmployee
    permission_classes = [permissions.IsAuthenticated, IsEmployeeWithTimeoffPermission]

    def get_queryset(self):
        """
        Filter the queryset to include only TimeoffRequests made by the authenticated user.
        Applies additional filtering by status and pay period for 'list' actions.
        Includes select_related for optimized fetching of related data.
        """
        user = self.request.user
        queryset = TimeoffRequest.objects.filter(employee=user).select_related(
            'employee', 'requested_leave_type', 'reference_pay_period'
        )

        if self.action == 'list':
            status_param = self.request.query_params.get('status', 'pending')
            queryset = queryset.filter(status__iexact=status_param)

            pay_period_id = self.request.query_params.get('pay_period_id')
            if pay_period_id:
                try:
                    pay_period_id = int(pay_period_id)
                    queryset = queryset.filter(reference_pay_period__id=pay_period_id)
                except ValueError:
                    queryset = TimeoffRequest.objects.none()
            else:
                current_pay_period = PayPeriod.get_pay_period_for_date(timezone.now())
                if current_pay_period:
                    queryset = queryset.filter(reference_pay_period=current_pay_period)
                else:
                    queryset = TimeoffRequest.objects.none()

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """
        Save the time-off request with the authenticated user as the employee.
        Ensure user has a UserProfile.
        """
        try:
            UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("User profile not found.")
        serializer.save()

    def perform_update(self, serializer):
        """
        Ensure updates are performed only by employees with a valid UserProfile.
        """
        try:
            UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise PermissionDenied("User profile not found.")
        serializer.save()

    def get_serializer_context(self):
        """
        Pass request context to serializer for user-specific validations.
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
        