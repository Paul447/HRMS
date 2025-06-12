# Create your views here.
from django.shortcuts import  redirect
from rest_framework import viewsets
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

# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
@method_decorator(csrf_protect, name='dispatch')
class PTORequestsViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing PTO requests.
    Provides CRUD operations for PTO requests, with specific handling
    for user-specific access and status-based filtering.
    """
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters PTO requests to only show those belonging to the authenticated user.
        For 'list' action, supports filtering by 'status' and 'pay_period_id'.
        For 'retrieve', 'update', 'destroy' actions, allows fetching any of the user's requests.
        """
        user = self.request.user
        queryset = PTORequests.objects.filter(user=user)

        # Apply filters only for the 'list' action
        if self.action == 'list':
            # Get status from query parameters, default to 'pending' for the primary list
            status_param = self.request.query_params.get('status', 'pending')
            queryset = queryset.filter(status__iexact=status_param)

            # Get pay_period_id from query parameters
            pay_period_id = self.request.query_params.get('pay_period_id')

            if pay_period_id:
                try:
                    pay_period_id = int(pay_period_id)
                    queryset = queryset.filter(pay_period__id=pay_period_id)
                except ValueError:
                    # If invalid pay_period_id, return empty for safety on list views
                    queryset = PTORequests.objects.none()
            else:
                # If no pay_period_id is provided for list, filter by the current pay period
                now = timezone.now()
                current_pay_period = PayPeriod.get_pay_period_for_date(now)
                if current_pay_period:
                    queryset = queryset.filter(pay_period=current_pay_period)
                else:
                    # If no current pay period found, return an empty queryset for list
                    queryset = PTORequests.objects.none()

        # Always order by created_at for consistency
        return queryset.order_by('-created_at')


    def perform_create(self, serializer):
        """
        Automatically assigns the authenticated user and the current pay period
        to the PTO request upon creation.
        """
        now = timezone.now()
        current_pay_period = PayPeriod.get_pay_period_for_date(now)

        if not current_pay_period:
            # Handle the case where no current pay period exists
            raise ValidationError({"detail": "No active pay period found for today's date. Cannot submit request."})

        serializer.save(user=self.request.user, pay_period=current_pay_period)

    def perform_update(self, serializer):
        """
        Ensures a user can only update their own PTO requests.
        """
        # Check if the instance belongs to the current user before saving
        if serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You do not have permission to edit this request."},
                status=status.HTTP_403_FORBIDDEN
            )
        # Add logic to prevent updates to requests from past pay periods if desired
        # Example:
        # now = timezone.now()
        # if serializer.instance.pay_period and serializer.instance.pay_period.end_date < now.date():
        #     raise ValidationError({"detail": "Cannot update requests from past pay periods."})
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
        # Add logic to prevent deletion of requests from past pay periods if desired
        # Example:
        # now = timezone.now()
        # if instance.pay_period and instance.pay_period.end_date < now.date():
        #     raise ValidationError({"detail": "Cannot delete requests from past pay periods."})
        instance.delete()
        # TODO : Need to remove the logic of viewing all of the details by the pay period from this because it is still in here,, Also View the pending request in the history because, noting should be hidden.

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
                # Handle invalid pay_period_id gracefully.
                approved_requests_queryset = PTORequests.objects.none()
                rejected_requests_queryset = PTORequests.objects.none()
        else:
            # If no pay_period_id is provided, filter by the current pay period
            now = timezone.now()
            current_pay_period = PayPeriod.get_pay_period_for_date(now)
            if current_pay_period:
                approved_requests_queryset = approved_requests_queryset.filter(pay_period=current_pay_period)
                rejected_requests_queryset = rejected_requests_queryset.filter(pay_period=current_pay_period)
            else:
                approved_requests_queryset = PTORequests.objects.none()
                rejected_requests_queryset = PTORequests.objects.none()


        # Serialize the data
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
                    # If invalid pay_period_id, return empty for safety on list views
                    queryset = PTORequests.objects.none()
        else:
                # If no pay_period_id is provided for list, filter by the current pay period
                now = timezone.now()
                current_pay_period = PayPeriod.get_pay_period_for_date(now)
                if current_pay_period:
                    queryset = queryset.filter(pay_period=current_pay_period)
                else:
                    # If no current pay period found, return an empty queryset for list
                    queryset = PTORequests.objects.none()

        # Always order by created_at for consistency
        return queryset.order_by('-created_at')

        
        


class PTORequestsView(TemplateView, LoginRequiredMixin):
    template_name = 'ptorequest.html'
    login_url = 'frontend_login'  # Redirect to the login page if not authenticated
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context data here if needed
        return context

class TimeoffDetailsView(TemplateView, LoginRequiredMixin):
    template_name = 'timeoff_details.html'
    login_url = 'frontend_login'  # Redirect to the login page if not authenticated
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context data here if needed
        return context

class GetPastPTORequestsView(TemplateView, LoginRequiredMixin):
    template_name = 'get_past_pto_request_view.html'
    login_url = 'frontend_login'  # Redirect to the login page if not authenticated
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context data here if needed
        return context



# TODO Add the Leave Management Where the Admin can Approve or Reject the PTO Requests, Also make it enable to do the filter so, only let the user admin view the leave of this and upcomming pay period, Filter according to the department, don't show the leave automatically let the user search for it. Also let superuser view the balance on the type of the leave they have asked for.
# TODO Create the view which return the Leave Balance of all the employees, and make it filterable by the department, show the currently running balance of the user.
# Working on this # Refactor --> Create the tooltip to view the entire reason of the request. # DONE Let the normal user view only his/her own leave requests, based on the pay period, and also let the user filter the leave request based on the pay period, check for the intial parameter in the URL if there is no parameter then show the current pay period leave requests, if there is a parameter then show the leave requests for that pay period.
# TODO Let the SuperUser edit the leave request comment box to add the comment for the leave request.
# TODO Create the logic for leave request approval and rejection, if rejection don't do anything, if approved, create the logic to deduct the leave balance from the user on the basis of the leave type, and also update the leave request status to approved,