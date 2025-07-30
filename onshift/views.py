from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from timeclock.models import Clock
from rest_framework.permissions import BasePermission
from .serializer import UserOnShiftClockSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filter import OnsShiftClockFilter  # Import your custom filter

# Removed incorrect import of IsAuthenticated from django.permissions
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import APIView

class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


# Create your views here.


class UserClockOnShiftViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset to retrieve the clock-in/out data for users currently on shift.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = UserOnShiftClockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OnsShiftClockFilter
    queryset = Clock.objects.filter(clock_out_time__isnull=True).order_by("user__first_name", "user__last_name")
    
    def list(self, request, *args, **kwargs):
        """
        List all users currently on shift (i.e., clocked in but not out).
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OnShiftFrontendView(APIView):
    """
    A frontend view to display users currently on shift.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    template_name = "onshift.html"
    renderer_classes = [TemplateHTMLRenderer]
    login_url = "hrmsauth:frontend_login"
    versioning_class = None  # Disable versioning for this view
    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        """
        Render the on-shift template.
        """
        return Response(template_name=self.template_name)
