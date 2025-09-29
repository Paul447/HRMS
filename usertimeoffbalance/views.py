from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from unverifiedsickleave.models import SickLeaveBalance
from .serializer import TimeoffBalanceSerializer
from .pagination import TimeoffBalancePagination
from rest_framework import filters
from timeoff_management.views import IsManagerOfDepartment
from rest_framework import permissions
from department.models import UserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect



class TimeoffBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving time-off balances, visible to managers and superusers only.
    """
    serializer_class = TimeoffBalanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOfDepartment]
    pagination_class = TimeoffBalancePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name"]

    def get_queryset(self):
        user = self.request.user
        base_queryset = SickLeaveBalance.objects.select_related(
            "user",
            "user__pto_balance",
            "user__pto_balance__accrual_rate",
            "user__profile",
            "user__profile__employee_type",
            "user__profile__payfreq",
            # "user__profile__tenure",
        )


        if user.is_superuser:
            return base_queryset

        user_profile = getattr(user, "userprofile", None)
        if user_profile and user_profile.is_manager:
            return base_queryset.filter(user__userprofile__department=user_profile.department)

        return base_queryset.none()


class TimeOffBalanceTemplate(APIView):
    """
    A TemplateView for rendering the time-off balance page.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "time_off_balance.html"
    login_url = "hrmsauth:frontend_login"
    versioning_class = None  # Disable versioning for this view

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)
    
    
    def get(self, request, *args, **kwargs):
        """
        Render the time-off balance template.
        """
        return Response(template_name=self.template_name)


