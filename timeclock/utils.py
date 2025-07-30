# utils.py
from datetime import datetime, timedelta
import pytz
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from timeclock.models import Clock  # Assuming 'clock' is your app name for Clock model
from timeclock.serializer import ClockSerializer  # Assuming 'clock' is your app name for ClockSerializer


def get_pay_period_week_boundaries(pay_period, local_tz):
    """
    Calculates and returns the local and UTC start/end dates for Week 1 and Week 2
    within a given pay period.
    """
    pay_period_start_local_date = timezone.localtime(pay_period.start_date, timezone=local_tz).date()
    pay_period_end_local_date = timezone.localtime(pay_period.end_date, timezone=local_tz).date()

    week_1_start_local = pay_period_start_local_date
    week_1_end_local = pay_period_start_local_date + timedelta(days=6)

    week_2_start_local = pay_period_start_local_date + timedelta(days=7)
    week_2_end_local = pay_period_end_local_date

    # Convert local week boundaries to UTC datetimes for database query
    # Set time to start of day for start dates and end of day for end dates
    week_1_start_utc = local_tz.localize(datetime.combine(week_1_start_local, datetime.min.time())).astimezone(pytz.utc)
    week_1_end_utc = local_tz.localize(datetime.combine(week_1_end_local, datetime.max.time())).astimezone(pytz.utc)

    week_2_start_utc = local_tz.localize(datetime.combine(week_2_start_local, datetime.min.time())).astimezone(pytz.utc)
    week_2_end_utc = local_tz.localize(datetime.combine(week_2_end_local, datetime.max.time())).astimezone(pytz.utc)

    return {"local": {"week_1_start": week_1_start_local, "week_1_end": week_1_end_local, "week_2_start": week_2_start_local, "week_2_end": week_2_end_local}, "utc": {"week_1_start": week_1_start_utc, "week_1_end": week_1_end_utc, "week_2_start": week_2_start_utc, "week_2_end": week_2_end_utc}}


def _get_week_data(user_entries_for_pay_period, week_start_utc, week_end_utc):
    """
    Helper function to get aggregated data for a specific week.
    """
    week_entries_qs = user_entries_for_pay_period.filter(clock_in_time__gte=week_start_utc, clock_in_time__lte=week_end_utc, is_holiday=False)
    total_hours = week_entries_qs.aggregate(total_hours=Sum("hours_worked"))["total_hours"] or Decimal("0.00")
    return {"entries": ClockSerializer(week_entries_qs, many=True).data, "total_hours": total_hours}


def get_user_weekly_summary(user, pay_period, week_boundaries_utc):
    """
    Aggregates clock and PTO data for a specific user across the two weeks
    of a given pay period.
    """
    user_entries_for_pay_period = Clock.objects.filter(user=user, clock_in_time__gte=pay_period.start_date, clock_in_time__lte=pay_period.end_date).order_by("clock_in_time")
    results = {}
    for i, week_num in enumerate([1, 2]):
        week_start_utc = week_boundaries_utc[f"week_{week_num}_start"]
        week_end_utc = week_boundaries_utc[f"week_{week_num}_end"]

        week_data = _get_week_data(user_entries_for_pay_period, week_start_utc, week_end_utc)

        results[f"week_{week_num}_entries"] = week_data["entries"]
        results[f"week_{week_num}_total_hours"] = week_data["total_hours"]
    active_clock_entry = user_entries_for_pay_period.filter(clock_out_time__isnull=True).first()
    active_clock_entry_data = ClockSerializer(active_clock_entry).data if active_clock_entry else None

    results["active_clock_entry"] = active_clock_entry_data
    results["current_status"] = "Clocked In" if active_clock_entry else "Clocked Out"

    return results
