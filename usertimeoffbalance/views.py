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
    ViewSet for retrieving time-off balances.
    Only managers and superusers can see results.
    """
    serializer_class = TimeoffBalanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOfDepartment]
    pagination_class = TimeoffBalancePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name"]

    def get_queryset(self):
        return self._build_queryset()

    def _build_queryset(self):
        user = self.request.user

        # Prefetch/select_related to avoid N+1 queries
        qs = (
            SickLeaveBalance.objects
            .select_related(
                "user",
                "user__profile",
                "user__pto_balance",
                "user__pto_balance__accrual_rate",
                "user__profile__employee_type",
                "user__profile__payfreq",
            )
        )

        # Superusers see everything
        if user.is_superuser:
            return qs

        # Managers see balances for their department
        profile = getattr(user, "profile", None)
        if profile and profile.is_manager:
            return qs.filter(user__profile__department=profile.department)

        # Everyone else sees nothing
        return qs.none()



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


