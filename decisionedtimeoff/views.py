from django.shortcuts import render
from .serializer import DecisionedTimeOffSerializer
from rest_framework import viewsets
from timeoffreq.models import TimeoffRequest
from rest_framework import permissions
from .permissions import IsManagerOfDepartment
from department.models import UserProfile
from django.utils import timezone
from datetime import datetime, time
import pytz
from rest_framework import filters
from .pagination import DecisionedTimeOffPagination 
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer


class DecisionedTimeOffViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing decisioned time off requests.
    """

    serializer_class = DecisionedTimeOffSerializer
    pagination_class = DecisionedTimeOffPagination  # Use default pagination or set your custom one if needed
    filter_backends = [filters.SearchFilter]  # Enable search functionality
    search_fields = ["employee__first_name", "employee__last_name", "requested_leave_type__leave_type__name"]  # Fields to search against
    
    def get_permissions(self):
        """
        Superusers only require IsAuthenticated.
        Others must also be managers.
        """
        if self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManagerOfDepartment()]

    def get_queryset(self):
        """
        Dynamically filters decisioned time-off requests from today onwards (Chicago local time).
        Superusers see all, managers see their department, others see nothing.
        """
        # 1. Calculate "start of today" in UTC based on Chicago timezone
        local_tz = pytz.timezone("America/Chicago")
        now_local = timezone.now().astimezone(local_tz)
        today_local_date = now_local.date()
        start_of_today_local = datetime.combine(today_local_date, time.min)
        start_of_today_localized = local_tz.localize(start_of_today_local)
        start_of_today_utc = start_of_today_localized.astimezone(pytz.UTC)

        # 2. Build base queryset
        base_queryset = TimeoffRequest.objects.filter(
            status__in=["approved", "rejected"],
            start_date_time__gte=start_of_today_utc
        ).select_related("employee", "requested_leave_type__leave_type").order_by("-reviewed_at")

        user = self.request.user

        if not user.is_authenticated:
            return TimeoffRequest.objects.none()

        if user.is_superuser:
            return base_queryset

        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile and user_profile.is_manager:
            return base_queryset.filter(
                employee__userprofile__department=user_profile.department
            )

        return TimeoffRequest.objects.none()
    
class DecisionedTimeOffViewSetFrontend(APIView):
    """
    A TemplateView for rendering the decisioned time-off page.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [permissions.IsAuthenticated]
    template_name = "decisioned_timeoff.html"  # Adjust the path to your template
    login_url = "hrmsauth:frontend_login"
    versioning_class = None

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)
    
    def get(self, request, *args, **kwargs):
        """
        Render the decisioned time-off template.
        """
        return Response(template_name=self.template_name)
