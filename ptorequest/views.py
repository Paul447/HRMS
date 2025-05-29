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
        return PTORequests.objects.filter(user=self.request.user, status='pending').order_by('-created_at')

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

        approved_requests = PTORequests.objects.filter(user=user, status__iexact='approved').order_by('-created_at')
        rejected_requests = PTORequests.objects.filter(user=user, status__iexact='rejected').order_by('-created_at')

        # Serialize the data
        approved_data = self.get_serializer(approved_requests, many=True).data
        rejected_data = self.get_serializer(rejected_requests, many=True).data

        return Response({
            "approved_requests": approved_data,
            "rejected_requests": rejected_data
        })





class PTORequestsView(TemplateView):
    template_name = 'ptorequest.html'
    def dispatch(self, request, *args, **kwargs):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)

        if not access_token:
            return redirect(reverse('frontend_login'))

        try:
            AccessToken(access_token).verify()
        except TokenError:
            return redirect(reverse('frontend_login'))

        return super().dispatch(request, *args, **kwargs)

class TimeoffDetailsView(TemplateView):
    template_name = 'timeoff_details.html'
    
    def dispatch(self, request, *args, **kwargs):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)

        if not access_token:
            return redirect(reverse('frontend_login'))

        try:
            AccessToken(access_token).verify()
        except TokenError:
            return redirect(reverse('frontend_login'))

        return super().dispatch(request, *args, **kwargs)