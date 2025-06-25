from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import TimeoffRequest
from .serializer import TimeoffRequestSerializerEmployee, TimeoffApproveRejectManager
from department.models import UserProfile
from payperiod.models import PayPeriod  # Add this import for PayPeriod
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from leavetype.models import DepartmentBasedLeaveType
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model  # Import to get the User model

User = get_user_model()
        
 # Best practice for getting the active user model

class IsEmployeeWithTimeoffPermission(permissions.BasePermission):
    """
    Custom permission to allow a user to manipulate (or view) a time-off request
    ONLY IF they are the employee associated with the request
    AND their UserProfile's 'is_time_off' field is True.
    This applies to ALL HTTP methods (GET, POST, PUT, DELETE, etc.).
    """
    message = "You must be the request's employee and have the 'Time Off' permission enabled in your profile to access this resource."

    def has_permission(self, request, view):
        # First, ensure the user is authenticated.
        if not request.user.is_authenticated:
            return False
        
        # Now, regardless of the method (safe or unsafe), check the user's profile.
        # This global permission means that a user MUST have 'is_time_off'
        # enabled just to interact with *any* time-off request resource.
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            # User must have a profile AND 'is_time_off' must be True
            return user_profile.is_time_off 
        except UserProfile.DoesNotExist:
            # If no user profile exists, or 'is_time_off' is False (handled by the return above)
            return False 

    def has_object_permission(self, request, view, obj):
        # For ANY method (including GET, HEAD, OPTIONS), the user must be the owner
        # AND have the 'is_time_off' permission.

        # 1. Check if the requesting user is the employee associated with the time-off request.
        is_owner = (obj.employee == request.user)
        
        # 2. Check if the user's UserProfile has 'is_time_off' set to True.
        # This check is duplicated from has_permission for robustness at the object level,
        # ensuring both conditions are met *for this specific object*.
        has_timeoff_profile_permission = False
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            has_timeoff_profile_permission = user_profile.is_time_off
        except UserProfile.DoesNotExist:
            has_timeoff_profile_permission = False # If no profile, no permission

        # The user must be the owner AND have the 'is_time_off' permission for ANY action on this object.
        return is_owner and has_timeoff_profile_permission


class TimeoffRequestViewSetEmployee(viewsets.ModelViewSet):
    """
    ViewSet for managing TimeoffRequest instances for employees.
    Supports listing, retrieving, creating, updating, and deleting time-off requests.
    Restricted to employee-owned requests with 'is_time_off' permission.
    """
    permission_classes = [IsEmployeeWithTimeoffPermission]
    serializer_class = TimeoffRequestSerializerEmployee

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
    @action(detail=False, methods=['get'], url_path='summary')
    def approved_and_rejected(self, request):
        """
        Returns a combined list of approved and rejected time-off requests
        for the authenticated user, optionally filtered by pay period.
        """
        user = self.request.user
        pay_period_id = self.request.query_params.get('pay_period_id')

        # Base querysets for approved and rejected requests
        approved_requests_queryset = TimeoffRequest.objects.filter(
            employee=user, # Corrected field name
            status__iexact='approved'
        ).select_related(
            'employee', 'requested_leave_type', 'reference_pay_period', # Optimizing query
            'requested_leave_type__leave_type', 'requested_leave_type__department'
        )

        rejected_requests_queryset = TimeoffRequest.objects.filter(
            employee=user, # Corrected field name
            status__iexact='rejected'
        ).select_related(
            'employee', 'requested_leave_type', 'reference_pay_period', # Optimizing query
            'requested_leave_type__leave_type', 'requested_leave_type__department'
        )

        # Apply pay period filtering
        if pay_period_id:
            try:
                pay_period_id = int(pay_period_id)
                approved_requests_queryset = approved_requests_queryset.filter(reference_pay_period__id=pay_period_id) # Corrected field name
                rejected_requests_queryset = rejected_requests_queryset.filter(reference_pay_period__id=pay_period_id) # Corrected field name
            except ValueError:
                # If pay_period_id is invalid, return empty lists immediately
                return Response({
                    "approved_requests": [],
                    "rejected_requests": []
                })
        else:
            # If no pay_period_id is provided, filter by the current pay period
            now = timezone.now()
            current_pay_period = PayPeriod.get_pay_period_for_date(now)
            if current_pay_period:
                approved_requests_queryset = approved_requests_queryset.filter(reference_pay_period=current_pay_period) # Corrected field name
                rejected_requests_queryset = rejected_requests_queryset.filter(reference_pay_period=current_pay_period) # Corrected field name
            else:
                # If no current pay period found, return empty lists
                return Response({
                    "approved_requests": [],
                    "rejected_requests": []
                })

        # Serialize the filtered querysets
        # Use self.get_serializer for proper context passing
        approved_data = self.get_serializer(approved_requests_queryset.order_by('-created_at'), many=True).data
        rejected_data = self.get_serializer(rejected_requests_queryset.order_by('-created_at'), many=True).data

        # Return the combined data in the desired format
        return Response({
            "approved_requests": approved_data,
            "rejected_requests": rejected_data
        })

class PastTimeOffRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for employees to view past time-off requests.
    
    """
    serializer_class = TimeoffRequestSerializerEmployee
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = TimeoffRequest.objects.filter(employee=user)
        pay_period_id = self.request.query_params.get('pay_period_id')
        queryset = queryset.exclude(status__iexact='pending')

        if pay_period_id:
            try:
                pay_period_id = int(pay_period_id)
                queryset = queryset.filter(reference_pay_period__id=pay_period_id)
            except ValueError:
                queryset = TimeoffRequest.objects.none()
        else:
            now = timezone.now()
            current_pay_period = PayPeriod.get_pay_period_for_date(now)
            if current_pay_period:
                queryset = queryset.filter(reference_pay_period=current_pay_period)
            else:
                queryset = TimeoffRequest.objects.none()

        return queryset.order_by('-created_at')

class DepartmentLeaveTypeDropdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get user's departments
        user_department_ids = UserProfile.objects.filter(user=user).values_list('department__id', flat=True)

        # Filter leave types for those departments
        leave_types = DepartmentBasedLeaveType.objects.filter(
            department__id__in=user_department_ids
        ).select_related('department', 'leave_type')

        # Return simplified JSON
        data = [
            {
                "id": lt.id,
                "display_name": f"{lt.leave_type.name}"
            }
            for lt in leave_types
        ]
        return Response(data)



class TimeOffRequestView(TemplateView, LoginRequiredMixin):
    template_name = 'timeoff_request.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class TimeOffRequestDetailsView(TemplateView, LoginRequiredMixin):

    template_name = 'timeoff_request_view.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class GetPastTimeOffRequestsView(TemplateView, LoginRequiredMixin):
    template_name = 'get_past_timeoff_requests_view.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context