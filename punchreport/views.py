# Punch Report Views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import pytz
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from payperiod.models import PayPeriod
from payperiod.serializer import PayPeriodSerializerForClockPunchReport
from .utils import get_pay_period_week_boundaries, get_user_weekly_summary

# Create your views here.
class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
        
class ClockInOutPunchReportView(TemplateView):
    """
    A view to render the clock in/out punch report page.
    This is a frontend view that will be served to users.
    """
    template_name = 'clock_in_out_punch_report.html'
    permission_classes = [IsAuthenticated]

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class ClockDataViewSet(viewsets.ViewSet):
    """
    A ViewSet for superusers to retrieve aggregated clock data for all users
    within a specified pay period. Normal authenticated users can access their
    own aggregated clock data for a specified pay period.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        pay_period_id = request.query_params.get('pay_period_id')

        if not pay_period_id:
            return Response(
                {"detail": "Please provide a 'pay_period_id' query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pay_period = PayPeriod.objects.get(id=pay_period_id)
        except PayPeriod.DoesNotExist:
            return Response(
                {"detail": f"Pay period with ID {pay_period_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        local_tz = pytz.timezone(settings.TIME_ZONE)
        week_boundaries = get_pay_period_week_boundaries(pay_period, local_tz)

        if request.user.is_superuser:
            users_to_report = User.objects.all().order_by('first_name', 'last_name')
        else:
            users_to_report = User.objects.filter(id=request.user.id)

        all_users_data = []
        for user_obj in users_to_report:
            user_data = get_user_weekly_summary(user_obj, pay_period, week_boundaries["utc"])
            all_users_data.append({
                "user_id": user_obj.id,
                "username": user_obj.username,
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                **user_data
            })

        return Response({
            "message": "Aggregated clock data for pay period retrieved successfully.",
            "pay_period": PayPeriodSerializerForClockPunchReport(pay_period).data,
            "week_boundaries": week_boundaries["local"],
            "users_clock_data": all_users_data,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminUser])
    def pay_periods(self, request):
        """
        Retrieves a list of all available pay periods up to and including today's date.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)
        today_local_date = timezone.localtime(timezone.now(), timezone=local_tz).date()
        end_of_today_local = local_tz.localize(datetime.combine(today_local_date, datetime.max.time()))
        end_of_today_utc = end_of_today_local.astimezone(pytz.utc)

        pay_periods = PayPeriod.objects.filter(
            start_date__lte=end_of_today_utc
        ).order_by('-start_date')

        serializer = PayPeriodSerializerForClockPunchReport(pay_periods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)