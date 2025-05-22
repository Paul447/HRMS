# Create your views here.
from django.shortcuts import  redirect
from rest_framework import viewsets
from .models import PTORequests
from .serializer import PTORequestsSerializer
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, TokenError


# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
class PTORequestsViewSet(viewsets.ModelViewSet):
    queryset = PTORequests.objects.all()
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Optionally limit to the current user's requests
        return None
    def destroy(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)  # allow this if you want users to see their requests
    def update(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)
    def partial_update(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)

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
