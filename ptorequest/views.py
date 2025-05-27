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


# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
@method_decorator(csrf_protect, name='dispatch')
class PTORequestsViewSet(viewsets.ModelViewSet):
    queryset = PTORequests.objects.all()
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        """
        Override the get_queryset method to filter PTO requests by the authenticated user.
        This ensures that users can only see their own PTO requests.
        """
        user = self.request.user
        
        return PTORequests.objects.filter(user=user)
    def perform_create(self, serializer):
    
        """
        Override the perform_create method to automatically assign the authenticated user
        to the PTO request when it is created.
        """
        user = self.request.user
        serializer.save(user=user)
    
    def perform_update(self, serializer):
        """
        Automatically assigns the requesting user to the PTO request during update,
        and ensures the instance being updated belongs to the user.
        """
        # Ensure the user can only update their own requests
        if serializer.instance.user != self.request.user:
            # You might want to raise a PermissionDenied or return a 403 Forbidden here
            # Depending on how strict you want this to be. For now, we'll let
            # the default permission checks handle it (e.g., if get_queryset already filters).
            # However, explicitly checking here adds an extra layer of security.
            return Response({"detail": "You do not have permission to edit this request."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save(user=self.request.user)

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