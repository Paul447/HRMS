# Create your views here.
from django.shortcuts import  redirect
from rest_framework import viewsets
from .models import PTORequests
from .serializer import PTORequestsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, TokenError
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
        Filters PTO requests to only show those belonging to the authenticated user
        and with a 'pending' status by default for list views.
        """
        # Ensure the request is for the authenticated user and only 'pending' requests initially.
        # This is suitable for a primary 'pending' list.
        # Get the current user's pay period to filter requests accordingly.
        now = timezone.now()
        current_pay_period = PayPeriod.get_pay_period_for_date(now)
        if current_pay_period:
            return PTORequests.objects.filter(
                user=self.request.user,
                status='pending',
                pay_period=current_pay_period
            ).order_by('-created_at')
        # return PTORequests.objects.filter(user=self.request.user, status='pending').order_by('-created_at')

    def perform_create(self, serializer):
        """
        Automatically assigns the authenticated user to the PTO request upon creation.
        """
        serializer.save(user=self.request.user)

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
        serializer.save(user=self.request.user) # User field remains unchanged, but explicit for clarity

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
        Accessible via `/api/ptorequests/approved-and-rejected/`.
        """
        user = request.user

        # Get the current pay period for the user
        now = timezone.now()
        current_pay_period = PayPeriod.get_pay_period_for_date(now) 

        approved_requests = PTORequests.objects.filter(user=user, status__iexact='approved', pay_period=current_pay_period).order_by('-created_at')
        rejected_requests = PTORequests.objects.filter(user=user, status__iexact='rejected', pay_period=current_pay_period).order_by('-created_at')

        # Serialize the data
        approved_data = self.get_serializer(approved_requests, many=True).data
        rejected_data = self.get_serializer(rejected_requests, many=True).data

        return Response({
            "approved_requests": approved_data,
            "rejected_requests": rejected_data
        })





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
    
    
    
    

# TODO Add the Leave Management Where the Admin can Approve or Reject the PTO Requests, Also make it enable to do the filter so, only let the user admin view the leave of this and upcomming pay period, Filter according to the department, don't show the leave automatically let the user search for it. Also let superuser view the balance on the type of the leave they have asked for.
# TODO Create the view which return the Leave Balance of all the employees, and make it filterable by the department, show the currently running balance of the user. 
 # Working on this # TODO Let the normal user view only his/her own leave requests, based on the pay period, and also let the user filter the leave request based on the pay period, check for the intial parameter in the URL if there is no parameter then show the current pay period leave requests, if there is a parameter then show the leave requests for that pay period.
# TODO Let the SuperUser edit the leave request comment box to add the comment for the leave request.
# TODO Create the logic for leave request approval and rejection, if rejection don't do anything, if approved, create the logic to deduct the leave balance from the user on the basis of the leave type, and also update the leave request status to approved,