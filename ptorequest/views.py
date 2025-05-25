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
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator


# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
@method_decorator(csrf_protect, name='dispatch')
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
    # def create(self, request, *args, **kwargs):
    #     # Custom logic for creating a PTO request --> Invalid this logic because the users can get the advance payed for their pto in breaks check for the users paytype request and the check for the off balance requested by the user if balance is not sufficient then return the error message to the user
    #     # You can implement your custom logic here
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

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
