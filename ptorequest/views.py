# Create your views here.
from rest_framework import viewsets, permissions
from .models import PTORequests
from .serializer import PTORequestsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from payperiod.models import PayPeriod
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from department.models import UserProfile # Keep UserProfile import for IsTimeOffUser
from notificationapp.models import Notification
from django.contrib.contenttypes.models import ContentType

import logging

logger = logging.getLogger(__name__)

# Import the new functions from your services file
from .services import send_custom_email, get_supervisor_for_user

# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
class IsTimeOffUser(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'is_time_off' profile flag
    to create PTO requests.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            user_profile = request.user.userprofile
            return user_profile.is_time_off
        except UserProfile.DoesNotExist:
            return False

@method_decorator(csrf_protect, name='dispatch')
class PTORequestsViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing PTO requests.
    Provides CRUD operations for PTO requests, with specific handling
    for user-specific access and status-based filtering.
    """
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated, IsTimeOffUser]

    def get_queryset(self):
        user = self.request.user
        queryset = PTORequests.objects.filter(user=user)

        if self.action == 'list':
            status_param = self.request.query_params.get('status', 'pending')
            queryset = queryset.filter(status__iexact=status_param)

            pay_period_id = self.request.query_params.get('pay_period_id')

            if pay_period_id:
                try:
                    pay_period_id = int(pay_period_id)
                    queryset = queryset.filter(pay_period__id=pay_period_id)
                except ValueError:
                    queryset = PTORequests.objects.none()
            else:
                now = timezone.now()
                current_pay_period = PayPeriod.get_pay_period_for_date(now)
                if current_pay_period:
                    queryset = queryset.filter(pay_period=current_pay_period)
                else:
                    queryset = PTORequests.objects.none()

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """
        Automatically assigns the authenticated user and the current pay period
        to the PTO request upon creation.
        Handles notification creation and email sending for the supervisor.
        """
        now = timezone.now()
        current_pay_period = PayPeriod.get_pay_period_for_date(now)

        if not current_pay_period:
            raise ValidationError({"detail": "No active pay period found for today's date. Cannot submit request."})

        serializer.save(user=self.request.user, pay_period=current_pay_period)
        pto_request_instance = serializer.instance

        requester = self.request.user
        supervisor_profile, supervisor_email = get_supervisor_for_user(requester)

        if supervisor_profile and supervisor_email:
            try:
                # Create in-app notification
                Notification.objects.create(
                    actor=requester,
                    recipient=supervisor_profile.user,
                    verb='Time Off request',
                    content_type=ContentType.objects.get_for_model(pto_request_instance),
                    object_id=pto_request_instance.id,
                    description=f"{requester.username} has created a Time Off request."
                )
                logger.info(f"In-app notification created for supervisor {supervisor_profile.user.username}.")

                # Prepare email context
                email_context = {
                    'requester_name': requester.get_full_name(),
                    'leave_type': serializer.validated_data.get('leave_type', 'N/A'),
                    'start_date': serializer.validated_data.get('start_date_time'),
                    'end_date': serializer.validated_data.get('end_date_time'),
                    'total_hours': serializer.validated_data.get('total_hours', 0),
                    'reason': serializer.validated_data.get('reason', 'No reason provided.'),
                }

                # Send email
                send_custom_email(
                    subject='New PTO Request Submitted',
                    recipient_list=[supervisor_email],
                    template_name='emails/pto_request_notification.html', # Create this template
                    context=email_context,
                    html_email=True
                )

            except Exception as e:
                logger.error(f"FATAL ERROR during notification/email sending for PTO request ID {pto_request_instance.id}: {e}", exc_info=True)
        else:
            logger.warning(
                f"Notification and email for PTO request from {requester.username} (ID: {pto_request_instance.id}) "
                f"were skipped due to missing supervisor or supervisor email."
            )

    def perform_update(self, serializer):
        """
        Ensures a user can only update their own PTO requests.
        """
        if serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You do not have permission to edit this request."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """
        Ensures a user can only delete their own PTO requests.
        """
        if instance.user != self.request.user:
            return Response(
                {"detail": "You do not have permission to delete this request."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=False, methods=['get'], url_path='approved-and-rejected')
    def approved_and_rejected(self, request):
        """
        Custom action to retrieve a list of a user's approved and rejected PTO requests.
        Supports filtering by 'pay_period_id' query parameter.
        Accessible via `/api/ptorequests/approved-and-rejected/`.
        """
        user = request.user
        pay_period_id = request.query_params.get('pay_period_id')

        approved_requests_queryset = PTORequests.objects.filter(user=user, status__iexact='approved')
        rejected_requests_queryset = PTORequests.objects.filter(user=user, status__iexact='rejected')

        if pay_period_id:
            try:
                pay_period_id = int(pay_period_id)
                approved_requests_queryset = approved_requests_queryset.filter(pay_period__id=pay_period_id)
                rejected_requests_queryset = rejected_requests_queryset.filter(pay_period__id=pay_period_id)
            except ValueError:
                approved_requests_queryset = PTORequests.objects.none()
                rejected_requests_queryset = PTORequests.objects.none()
        else:
            now = timezone.now()
            current_pay_period = PayPeriod.get_pay_period_for_date(now)
            if current_pay_period:
                approved_requests_queryset = approved_requests_queryset.filter(pay_period=current_pay_period)
                rejected_requests_queryset = rejected_requests_queryset.filter(pay_period=current_pay_period)
            else:
                approved_requests_queryset = PTORequests.objects.none()
                rejected_requests_queryset = PTORequests.objects.none()

        approved_data = self.get_serializer(approved_requests_queryset.order_by('-created_at'), many=True).data
        rejected_data = self.get_serializer(rejected_requests_queryset.order_by('-created_at'), many=True).data

        return Response({
            "approved_requests": approved_data,
            "rejected_requests": rejected_data
        })

class GetPTORequestsFromPastPayPeriodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet to retrieve PTO requests from past pay periods.
    This is a read-only view that allows users to see their past PTO requests.
    It filters by authenticated user and specifically for pay periods whose end_date is in the past.
    It does not include 'pending' requests as those should be processed by now.
    """
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PTORequests.objects.filter(user=user)
        pay_period_id = self.request.query_params.get('pay_period_id')
        queryset = queryset.exclude(status__iexact='pending')
        if pay_period_id:
                try:
                    pay_period_id = int(pay_period_id)
                    queryset = queryset.filter(pay_period__id=pay_period_id)
                except ValueError:
                    queryset = PTORequests.objects.none()
        else:
                now = timezone.now()
                current_pay_period = PayPeriod.get_pay_period_for_date(now)
                if current_pay_period:
                    queryset = queryset.filter(pay_period=current_pay_period)
                else:
                    queryset = PTORequests.objects.none()

        return queryset.order_by('-created_at')

class PTORequestsView(TemplateView, LoginRequiredMixin):
    template_name = 'ptorequest.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TimeoffDetailsView(TemplateView, LoginRequiredMixin):
    template_name = 'timeoff_details.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class GetPastPTORequestsView(TemplateView, LoginRequiredMixin):
    template_name = 'get_past_pto_request_view.html'
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context