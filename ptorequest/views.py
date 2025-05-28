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
from rest_framework.decorators import api_view, permission_classes


# Only dedicated to PTO Request Create Functionality Not for List, Update, Delete
from rest_framework.decorators import action
from rest_framework.response import Response

@method_decorator(csrf_protect, name='dispatch')
class PTORequestsViewSet(viewsets.ModelViewSet):
    queryset = PTORequests.objects.all()
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PTORequests.objects.filter(user=user, status='pending').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You do not have permission to edit this request."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='approved-and-rejected', permission_classes=[IsAuthenticated])
    def approved_and_rejected(self, request):
        user = request.user

        approved = PTORequests.objects.filter(user=user, status__iexact='approved').order_by('-created_at')
        rejected = PTORequests.objects.filter(user=user, status__iexact='rejected').order_by('-created_at')

        return Response({
            "approved_requests": PTORequestsSerializer(approved, many=True).data,
            "rejected_requests": PTORequestsSerializer(rejected, many=True).data
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