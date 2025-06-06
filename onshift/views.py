from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from timeclock.models import Clock
from rest_framework.permissions import BasePermission
from .serializer import UserOnShiftClockSerializer


class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# Create your views here.

class UserClockOnShiftView(ListAPIView):
    """
    A view to retrieve the clock-in/out data for users currently on shift.
    Also provides a custom action to get a detailed punch report for a specific user.
    """
    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = UserOnShiftClockSerializer

    def list(self, request, *args, **kwargs):
        """
        List all users currently on shift (i.e., those who have clocked in but not out).
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        """
        Retrieves clock data for users currently on shift.
        """
        return Clock.objects.filter(clock_out_time__isnull=True).order_by('user__first_name', 'user__last_name')




class OnShiftFrontendView(TemplateView):
    """
    A frontend view to display users currently on shift.
    """
    template_name = 'onshift.html'
    permission_classes = [IsAuthenticated, IsSuperuser]

    def get_context_data(self, **kwargs):

        return super().get_context_data(**kwargs)
