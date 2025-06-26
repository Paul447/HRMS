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
class TimeoffBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing time-off balances including both sick leave and PTO balances.
    """
    queryset = SickLeaveBalance.objects.all().select_related(
        'user', 
        'user__pto_balance',
        'user__pto_balance__employee_type',
        'user__pto_balance__pay_frequency',
        'user__pto_balance__year_of_experience',
        'user__pto_balance__accrual_rate'
    )
    serializer_class = TimeoffBalanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimeoffBalancePagination
    filter_backends = [filters.SearchFilter]  # No filters applied, can be extended if needed
    search_fields = ['user__first_name', 'user__last_name']  # Fields to search against
    
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
        Optionally filter queryset based on the authenticated user if they are not staff.
        """
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        return queryset
    

class TimeOffBalanceTemplate(TemplateView, LoginRequiredMixin):
    """
    A TemplateView for rendering the time-off balance page.
    """
    template_name = "time_off_balance.html"
    login_url = 'frontend_login'
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            return context