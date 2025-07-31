from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated , BasePermission
from rest_framework.viewsets import ViewSet
from django.utils import timezone
from django.conf import settings
import pytz
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import NotAuthenticated
from rest_framework.decorators import action
# Models and Serializers (assuming these are in the correct app imports)
from .models import Clock
from payperiod.models import PayPeriod
from .serializer import ClockSerializerPunch
from payperiod.serializer import PayPeriodSerializerForClockPunchReport
from decimal import Decimal


from django.shortcuts import render, redirect
# Import helper functions
from .utils import get_pay_period_week_boundaries, get_user_weekly_summary


class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class ClockInOutCreate(viewsets.GenericViewSet):
    """
    API endpoints for clocking in and clocking out.
    """
    # permission_classes = [IsAuthenticated]
    serializer_class = ClockSerializerPunch
    queryset = Clock.objects.none()  # Not used since we override actions

    def list(self, request):
        return Response({
            "available_actions": {
                "clock_in": request.build_absolute_uri("clock-in/"),
                "clock_out": request.build_absolute_uri("clock-out/")
            }
        })

    @action(detail=False, methods=['post'], url_path='clock-in')
    def clock_in(self, request):
        user = request.user
        current_time = timezone.now()

        # Check if there's already an active clock-in
        if Clock.objects.filter(user=user, clock_out_time__isnull=True).exists():
            return Response({
                "message": "Already clocked in. Please clock out first.",
                "error_code": "ALREADY_CLOCKED_IN"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find pay period
        pay_period = PayPeriod.get_pay_period_for_date(current_time)
        if not pay_period:
            return Response({
                "message": "No active pay period found for current time. Cannot clock in.",
                "error_code": "NO_PAY_PERIOD"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create clock entry
        clock_entry = Clock.objects.create(
            user=user,
            clock_in_time=current_time,
            clock_out_time=None,
            pay_period=pay_period
        )

        serializer = self.get_serializer(clock_entry)
        return Response({
            "message": "Successfully clocked in.",
            "clock_entry": serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='clock-out')
    def clock_out(self, request):
        user = request.user

        # Find active clock entry
        active_clock_entry = Clock.objects.filter(user=user, clock_out_time__isnull=True).first()
        if not active_clock_entry:
            return Response({
                "message": "No active clock-in entry found. Please clock in first.",
                "error_code": "NOT_CLOCKED_IN"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Clock out
        active_clock_entry.clock_out_time = timezone.now()
        active_clock_entry.save()

        serializer = self.get_serializer(active_clock_entry)
        return Response({
            "message": "Successfully clocked out.",
            "clock_entry": serializer.data
        }, status=status.HTTP_200_OK)


class UserClockDataAPIView(ViewSet):
    """
    API endpoint to retrieve a user's clock data for the current pay period,
    including current status and aggregated weekly hours.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        local_tz = pytz.timezone(settings.TIME_ZONE)
        today_local_datetime = timezone.localtime(timezone.now(), timezone=local_tz)
        today_local_date = today_local_datetime.date()  # Keep as date object for comparisons

        def format_date_for_display(date_obj):
            if not date_obj:
                return None

            return date_obj.strftime("%a, %b %d")

        print(f"Today's date (local): {today_local_date.strftime('%a, %b %d')}")

        pay_period = PayPeriod.get_pay_period_for_date(timezone.now())

        if not pay_period:
            # Format week_boundaries for the empty response as well
            return Response({"message": "No active pay period found for today.", "current_status": "No Pay Period", "pay_period": None, "week_number": None, "week_boundaries": {"week_1_start": None, "week_1_end": None, "week_2_start": None, "week_2_end": None}, "active_clock_entry": None, "week_1_entries": [], "week_1_total_hours": Decimal("0.00"), "week_2_entries": [], "week_2_total_hours": Decimal("0.00")}, status=status.HTTP_200_OK)

        # week_boundaries will contain date objects (or None) for 'local' and 'utc' keys
        week_boundaries = get_pay_period_week_boundaries(pay_period, local_tz)

        week_number = None
        # Use date objects for comparison, not formatted strings
        if week_boundaries["local"]["week_1_start"] and week_boundaries["local"]["week_1_start"] <= today_local_date <= week_boundaries["local"]["week_1_end"]:
            week_number = 1
        elif week_boundaries["local"]["week_2_start"] and week_boundaries["local"]["week_2_start"] <= today_local_date <= week_boundaries["local"]["week_2_end"]:
            week_number = 2

        user_data = get_user_weekly_summary(user, pay_period, week_boundaries["utc"])

        # Format week_boundaries for the final API response
        formatted_week_boundaries = {"week_1_start": format_date_for_display(week_boundaries["local"]["week_1_start"]), "week_1_end": format_date_for_display(week_boundaries["local"]["week_1_end"]), "week_2_start": format_date_for_display(week_boundaries["local"]["week_2_start"]), "week_2_end": format_date_for_display(week_boundaries["local"]["week_2_end"])}

        return Response({"message": "User clock data retrieved successfully.", "pay_period": PayPeriodSerializerForClockPunchReport(pay_period).data, "week_number": week_number, "week_boundaries": formatted_week_boundaries, **user_data}, status=status.HTTP_200_OK)  # Use the formatted boundaries here  # Unpack user_data directly into the response


class UserClockDataFrontendView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "clock_in_out.html"
    login_url = "hrmsauth:frontend_login"  # Django URL name
    versioning_class = None

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)



# TODO: Add the comment field in the clock model and allow users to add comments when clocking in/out, which will let the user know about what is the status.
