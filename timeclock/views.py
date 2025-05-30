# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.views.generic import TemplateView
from django.db import models
from django.db.models import Sum, Q
from django.db.models.functions import Cast
from django.db.models import DateField
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, date, datetime
from decimal import Decimal
import pytz

from .models import Clock
from payperiod.models import PayPeriod  
from .serializer import ClockSerializer, PayPeriodSerializer


class ClockInOutAPIView(APIView):
    """
    API endpoint for users to clock in and clock out.
    Handles the creation of new clock entries or updates existing open entries.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Check if the user has an active clock-in entry (clocked in but not clocked out)
        active_clock_entry = Clock.objects.filter(user=user, clock_out_time__isnull=True).first()

        if active_clock_entry:
            # User is clocked in, so clock them out
            active_clock_entry.clock_out_time = timezone.now()
            # The model's save method will handle `calculate_hours` and `pay_period` assignment
            active_clock_entry.save()
            
            serializer = ClockSerializer(active_clock_entry)
            return Response({
                "message": "Successfully clocked out.",
                "clock_entry": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # User is clocked out, so clock them in
            # Ensure a pay period exists for the current time
            current_time = timezone.now()
            pay_period = PayPeriod.get_pay_period_for_date(current_time)
            
            if not pay_period:
                return Response({
                    "message": "No active pay period found for current time. Cannot clock in.",
                    "error_code": "NO_PAY_PERIOD"
                }, status=status.HTTP_400_BAD_REQUEST)

            new_clock_entry = Clock.objects.create(
                user=user,
                clock_in_time=current_time,
                clock_out_time=None, # Initially null as user is just clocking in
                pay_period=pay_period # Assign directly during creation
            )
            serializer = ClockSerializer(new_clock_entry)
            return Response({
                "message": "Successfully clocked in.",
                "clock_entry": serializer.data
            }, status=status.HTTP_201_CREATED)


class UserClockDataAPIView(APIView):
    """
    API endpoint to retrieve a user's clock data for the current pay period,
    including current status and aggregated weekly hours.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get the configured local timezone
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Get today's date in the local timezone
        today_local_dt = timezone.localtime(timezone.now(), timezone=local_tz)
        today_local_date = today_local_dt.date()

        # Get the active pay period that includes today's date
        # PayPeriod.get_pay_period_for_date should work with a timezone-aware datetime.now()
        pay_period = PayPeriod.get_pay_period_for_date(timezone.now())

        if not pay_period:
            return Response({
                "message": "No active pay period found for today.",
                "current_status": "No Pay Period",
                "pay_period": None, # Ensure this is explicitly None if no pay period
                "week_number": None,
                "week_boundaries": {
                    "week_1_start": None, "week_1_end": None,
                    "week_2_start": None, "week_2_end": None,
                },
                "active_clock_entry": None,
                "week_1_entries": [],
                "week_1_total_hours": Decimal('0.00'),
                "week_2_entries": [],
                "week_2_total_hours": Decimal('0.00'),
            }, status=status.HTTP_200_OK)

        # Calculate week boundaries within the pay period based on local dates
        # Convert pay_period start/end to local timezone dates for consistent comparison
        # pay_period.start_date and end_date are UTC. Convert them to local dates.
        pay_period_start_local_date = timezone.localtime(pay_period.start_date, timezone=local_tz).date()
        pay_period_end_local_date = timezone.localtime(pay_period.end_date, timezone=local_tz).date()

        week_1_start_local = pay_period_start_local_date
        week_1_end_local = pay_period_start_local_date + timedelta(days=6)

        week_2_start_local = pay_period_start_local_date + timedelta(days=7)
        week_2_end_local = pay_period_end_local_date

        week_number = None
        if week_1_start_local <= today_local_date <= week_1_end_local:
            week_number = 1
        elif week_2_start_local <= today_local_date <= week_2_end_local:
            week_number = 2

        # Convert local week boundaries to UTC datetimes for database query
        # Set time to start of day for start dates and end of day for end dates
        # Make them timezone-aware in the local timezone, then convert to UTC
        week_1_start_utc = local_tz.localize(datetime.combine(week_1_start_local, datetime.min.time())).astimezone(pytz.utc)
        week_1_end_utc = local_tz.localize(datetime.combine(week_1_end_local, datetime.max.time())).astimezone(pytz.utc)

        week_2_start_utc = local_tz.localize(datetime.combine(week_2_start_local, datetime.min.time())).astimezone(pytz.utc)
        week_2_end_utc = local_tz.localize(datetime.combine(week_2_end_local, datetime.max.time())).astimezone(pytz.utc)


        # Retrieve user clock entries for the current pay period
        # Use pay_period start/end_date (which are UTC) for filtering database records
        user_entries_for_pay_period = Clock.objects.filter(
            user=user,
            clock_in_time__gte=pay_period.start_date, # These are already UTC, so fine
            clock_in_time__lte=pay_period.end_date
        ).order_by('-clock_in_time') # Order by most recent first

        # Check for active clock-in
        active_clock_entry = user_entries_for_pay_period.filter(clock_out_time__isnull=True).first()
        current_status = "Clocked In" if active_clock_entry else "Clocked Out"

        # Separate entries into Week 1 and Week 2 based on UTC clock-in times
        # by comparing against UTC week boundaries
        week_1_entries_qs = user_entries_for_pay_period.filter(
            clock_in_time__gte=week_1_start_utc,
            clock_in_time__lte=week_1_end_utc
        )

        week_2_entries_qs = user_entries_for_pay_period.filter(
            clock_in_time__gte=week_2_start_utc,
            clock_in_time__lte=week_2_end_utc
        )

        # Aggregate total hours for each week
        week_1_total_hours = week_1_entries_qs.aggregate(total_hours=Sum('hours_worked'))['total_hours'] or Decimal('0.00')
        week_2_total_hours = week_2_entries_qs.aggregate(total_hours=Sum('hours_worked'))['total_hours'] or Decimal('0.00')

        # Serialize entries for display
        week_1_serialized_entries = ClockSerializer(week_1_entries_qs, many=True).data
        week_2_serialized_entries = ClockSerializer(week_2_entries_qs, many=True).data
        
        # Serialize the active clock entry if it exists
        active_clock_entry_data = ClockSerializer(active_clock_entry).data if active_clock_entry else None

        return Response({
            "message": "User clock data retrieved successfully.",
            "current_status": current_status,
            "pay_period": PayPeriodSerializer(pay_period).data,
            "week_number": week_number,
            "week_boundaries": {
                # Return local dates for display on frontend
                "week_1_start": week_1_start_local.isoformat(),
                "week_1_end": week_1_end_local.isoformat(),
                "week_2_start": week_2_start_local.isoformat(),
                "week_2_end": week_2_end_local.isoformat(),
            },
            "active_clock_entry": active_clock_entry_data,
            "week_1_entries": week_1_serialized_entries,
            "week_1_total_hours": week_1_total_hours,
            "week_2_entries": week_2_serialized_entries,
            "week_2_total_hours": week_2_total_hours,
        }, status=status.HTTP_200_OK)


class CurrentPayPeriodAPIView(ListAPIView):
    """
    API endpoint to retrieve the current active pay period.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PayPeriodSerializer

    def get_queryset(self):
        # Retrieve the single active pay period that encompasses the current time
        current_pay_period = PayPeriod.get_pay_period_for_date(timezone.now())
        if current_pay_period:
            return PayPeriod.objects.filter(pk=current_pay_period.pk)
        return PayPeriod.objects.none() # Return an empty queryset if no pay period is found

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No active pay period found for current date."}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserClockDataFrontendView(TemplateView):
    template_name = 'clock_in_out.html'
    permission_classes = [IsAuthenticated] # Ensure only logged-in users can access

    # You might want to override get_context_data if you need to pass any initial
    # non-API-fetched data (though with an API-driven frontend, often not needed).
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Any context here would be for initial page load, before JS fetches data.
        # For a truly API-driven frontend, this is often minimal.
        return context