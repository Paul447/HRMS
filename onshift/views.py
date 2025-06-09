from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework import filters
from rest_framework.decorators import action
from timeclock.models import Clock
from rest_framework.permissions import BasePermission
from .serializer import UserOnShiftClockSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filter import OnsShiftClockFilter  # Import your custom filter

class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# Create your views here.

class UserClockOnShiftView(generics.ListAPIView):
    """
    A view to retrieve the clock-in/out data for users currently on shift.
    """
    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = UserOnShiftClockSerializer
    filter_backends = [DjangoFilterBackend] # Keep DjangoFilterBackend
    # === CRITICAL CHANGE: Use filterset_class instead of filterset_fields ===
    filterset_class = OnsShiftClockFilter # <--- POINT TO YOUR CUSTOM FILTERSET
    # The default ordering for the queryset will now be respected,
    # as there's no OrderingFilter to override it.
    queryset = Clock.objects.filter(clock_out_time__isnull=True).order_by('user__first_name', 'user__last_name')

    def list(self, request, *args, **kwargs):
        """
        List all users currently on shift (i.e., those who have clocked in but not out).
        """
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class OnShiftFrontendView(TemplateView):
    """
    A frontend view to display users currently on shift.
    """
    template_name = 'onshift.html'
    permission_classes = [IsAuthenticated, IsSuperuser]

    def get_context_data(self, **kwargs):

        return super().get_context_data(**kwargs)
