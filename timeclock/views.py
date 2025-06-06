from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.views.generic import TemplateView
from django.utils import timezone
from django.conf import settings
import pytz
# Models and Serializers (assuming these are in the correct app imports)
from .models import Clock
from payperiod.models import PayPeriod
from .serializer import ClockSerializer, PayPeriodSerializerForClockPunchReport
from decimal import Decimal
from rest_framework.permissions import BasePermission

# Import helper functions
from .utils import get_pay_period_week_boundaries, get_user_weekly_summary
class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class ClockInOutAPIView(APIView):
    """
    API endpoint for users to clock in and clock out.
    Handles the creation of new clock entries or updates existing open entries.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        active_clock_entry = Clock.objects.filter(user=user, clock_out_time__isnull=True).first()

        if active_clock_entry:
            active_clock_entry.clock_out_time = timezone.now()
            active_clock_entry.save() # Model's save handles hours and pay_period
            message = "Successfully clocked out."
            http_status = status.HTTP_200_OK
        else:
            current_time = timezone.now()
            pay_period = PayPeriod.get_pay_period_for_date(current_time)
            
            if not pay_period:
                return Response({
                    "message": "No active pay period found for current time. Cannot clock in.",
                    "error_code": "NO_PAY_PERIOD"
                }, status=status.HTTP_400_BAD_REQUEST)

            active_clock_entry = Clock.objects.create(
                user=user,
                clock_in_time=current_time,
                clock_out_time=None,
                pay_period=pay_period
            )
            message = "Successfully clocked in."
            http_status = status.HTTP_201_CREATED
            
        serializer = ClockSerializer(active_clock_entry)
        return Response({
            "message": message,
            "clock_entry": serializer.data
        }, status=http_status)


class UserClockDataAPIView(APIView):
    """
    API endpoint to retrieve a user's clock data for the current pay period,
    including current status and aggregated weekly hours.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        local_tz = pytz.timezone(settings.TIME_ZONE)
        today_local_date = timezone.localtime(timezone.now(), timezone=local_tz).date()

        pay_period = PayPeriod.get_pay_period_for_date(timezone.now())

        if not pay_period:
            return Response({
                "message": "No active pay period found for today.",
                "current_status": "No Pay Period",
                "pay_period": None,
                "week_number": None,
                "week_boundaries": {"week_1_start": None, "week_1_end": None, "week_2_start": None, "week_2_end": None},
                "active_clock_entry": None,
                "week_1_entries": [], "week_1_total_hours": Decimal('0.00'),
                "week_2_entries": [], "week_2_total_hours": Decimal('0.00'),
            }, status=status.HTTP_200_OK)

        week_boundaries = get_pay_period_week_boundaries(pay_period, local_tz)

        week_number = None
        if week_boundaries["local"]["week_1_start"] <= today_local_date <= week_boundaries["local"]["week_1_end"]:
            week_number = 1
        elif week_boundaries["local"]["week_2_start"] <= today_local_date <= week_boundaries["local"]["week_2_end"]:
            week_number = 2

        user_data = get_user_weekly_summary(user, pay_period, week_boundaries["utc"])
        
        return Response({
            "message": "User clock data retrieved successfully.",
            "pay_period": PayPeriodSerializerForClockPunchReport(pay_period).data,
            "week_number": week_number,
            "week_boundaries": week_boundaries["local"],
            **user_data # Unpack user_data directly into the response
        }, status=status.HTTP_200_OK)


class CurrentPayPeriodAPIView(ListAPIView):
    """
    API endpoint to retrieve the current active pay period.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PayPeriodSerializerForClockPunchReport

    def get_queryset(self):
        current_pay_period = PayPeriod.get_pay_period_for_date(timezone.now())
        return PayPeriod.objects.filter(pk=current_pay_period.pk) if current_pay_period else PayPeriod.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No active pay period found for current date."}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserClockDataFrontendView(TemplateView):
    template_name = 'clock_in_out.html'
    permission_classes = [IsAuthenticated]

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)






