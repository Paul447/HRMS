from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from unverifiedsickleave.models import SickLeaveBalance
from .serializer import TimeoffBalanceSerializer
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
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
    A ViewSet for viewing time-off balances including both sick leave and PTO balances.
    """

    queryset = SickLeaveBalance.objects.all().select_related("user", "user__pto_balance", "user__pto_balance__employee_type", "user__pto_balance__pay_frequency", "user__pto_balance__year_of_experience", "user__pto_balance__accrual_rate")
    serializer_class = TimeoffBalanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimeoffBalancePagination
    filter_backends = [filters.SearchFilter]  # No filters applied, can be extended if needed
    search_fields = ["user__first_name", "user__last_name"]  # Fields to search against

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Superusers will only require IsAuthenticated.
        """
        if self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManagerOfDepartment()]

    def get_queryset(self):
        """
        Optionally filter queryset based on the authenticated user.
        - Superusers get full access.
        - Managers see requests from their department.
        - Others see nothing.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset

        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_manager:
                return queryset.filter(user__userprofile__department=user_profile.department)
        except UserProfile.DoesNotExist:
            pass  # Fall through to return none

        return queryset.none()


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


