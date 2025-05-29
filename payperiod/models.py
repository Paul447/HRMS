from django.db import models
from django.utils import timezone
from datetime import timedelta, date, datetime, time
import pytz
from django.conf import settings

class PayPeriod(models.Model):
    """
    Represents a defined pay period with a start and end date/time.
    These fields are timezone-aware and stored in UTC by Django.
    """
    start_date = models.DateTimeField(
        verbose_name="Start Date and Time",
        help_text="The exact UTC date and time when this pay period begins."
    )
    end_date = models.DateTimeField(
        verbose_name="End Date and Time",
        help_text="The exact UTC date and time when this pay period ends. "
                  "Typically 23:59:59 on the end day of the period."
    )

    class Meta:
        verbose_name = "Pay Period"
        verbose_name_plural = "Pay Periods"
        ordering = ['start_date']
        # Consider adding a unique constraint if pay periods should not overlap
        # constraints = [models.UniqueConstraint(fields=['start_date', 'end_date'], name='unique_payperiod_range')]

    def __str__(self):
        """
        Returns a user-friendly string representation of the pay period,
        formatted for the local timezone defined in Django settings (America/Chicago).
        """
        chicago_tz = pytz.timezone('America/Chicago')
        chicago_start_date = self.start_date.astimezone(chicago_tz).date()
        chicago_end_date = self.end_date.astimezone(chicago_tz).date()
        return f"Pay Period: {chicago_start_date} to {chicago_end_date}"

    @classmethod
    def get_pay_period_for_date(cls, target_date_time):
        """
        Finds the single pay period that encompasses the given target date/time.
        Ensures the target_date_time is timezone-aware before querying.
        """
        default_tz = pytz.timezone(settings.TIME_ZONE)
        if timezone.is_naive(target_date_time):
            target_date_time = default_tz.localize(target_date_time)
        target_date_time = target_date_time.astimezone(pytz.utc)
        return cls.objects.filter(
            start_date__lte=target_date_time,
            end_date__gte=target_date_time
        ).first()

    @classmethod
    def get_pay_periods_up_to_today(cls):
        """
        Returns all pay periods that have an end date on or before today's date.
        "Today" is determined in the project's current local timezone (America/Chicago).
        """
        chicago_tz = pytz.timezone('America/Chicago')
        today_in_chicago = timezone.now().astimezone(chicago_tz).date()
        return cls.objects.filter(end_date__date__lte=today_in_chicago).order_by('end_date')
    @classmethod
    def generate_biweekly_pay_periods(cls, num_periods=35, start_from_date=None):
        """
        Generates a specified number of biweekly pay periods, ensuring they consistently
        start at 00:00:00 and end at 23:59:59 in the local timezone (settings.TIME_ZONE),
        even across DST transitions. Each period will span exactly 14 calendar days.
        """
        if num_periods <= 0:
            return 0, None

        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Determine the effective start datetime for the first new period
        # This will be in the local timezone, at midnight of its start day.
        effective_start_local_dt = None
        latest_pay_period = cls.objects.order_by('-end_date').first()

        if start_from_date:
            # If start_from_date is provided, ensure it's at midnight and localized
            if timezone.is_naive(start_from_date):
                effective_start_local_dt = local_tz.localize(start_from_date.replace(hour=0, minute=0, second=0, microsecond=0))
            else:
                effective_start_local_dt = start_from_date.astimezone(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        elif latest_pay_period:
            # The next period starts on the day AFTER the latest period's end date.
            # Get the end date in local time, get its date component, add 1 day, then set time to midnight.
            latest_end_date_local = latest_pay_period.end_date.astimezone(local_tz).date()
            next_start_date_component = latest_end_date_local + timedelta(days=1)
            effective_start_local_dt = local_tz.localize(
                datetime.combine(next_start_date_component, time(0, 0, 0))
            )
        else:
            # Default start date if no pay periods exist. Localize it to midnight.
            # Using current year + 1 (2025) as a default to avoid past dates.
            effective_start_local_dt = local_tz.localize(datetime(2025, 2, 9, 0, 0, 0))

        created_count = 0
        current_start_local_dt = effective_start_local_dt
        initial_generated_start_utc = None

        for i in range(num_periods):
            # Calculate the end *date* of the current pay period.
            # A 14-day period goes from day N to day N+13.
            current_end_date_component = current_start_local_dt.date() + timedelta(days=13)

            # Construct the local end datetime: this date at 23:59:59 in the local timezone
            try:
                current_end_local_dt = local_tz.localize(
                    datetime.combine(current_end_date_component, time(23, 59, 59))
                )
            except pytz.AmbiguousTimeError:
                current_end_local_dt = local_tz.localize(
                    datetime.combine(current_end_date_component, time(23, 59, 59)), is_dst=True
                )
            except pytz.NonExistentTimeError:
                # If 23:59:59 doesn't exist on this day due to DST, it means this day was shortened.
                # The correct end of the *calendar day* is effectively the end of the last full second
                # before the next day starts. We can achieve this by taking the *next day at midnight*
                # and subtracting 1 second.
                next_day_midnight = local_tz.localize(
                    datetime.combine(current_end_date_component + timedelta(days=1), time(0, 0, 0))
                )
                current_end_local_dt = next_day_midnight - timedelta(seconds=1)


            # Convert local timezone datetimes to UTC for saving to the database
            start_date_utc = current_start_local_dt.astimezone(pytz.utc)
            end_date_utc = current_end_local_dt.astimezone(pytz.utc)

            # Overlap check (using UTC for consistency with database storage)
            # Use <= and >= for inclusive checks to prevent tiny gaps/overlaps at exact boundaries
            if cls.objects.filter(
                start_date__lte=end_date_utc,
                end_date__gte=start_date_utc
            ).exclude(pk__in=cls.objects.filter(start_date=start_date_utc, end_date=end_date_utc)).exists():
                 # Log or raise an error if an overlap is found, but for now, we'll break
                 print(f"Overlap detected for period {start_date_utc} to {end_date_utc}. Stopping generation.")
                 break

            cls.objects.create(
                start_date=start_date_utc,
                end_date=end_date_utc
            )
            if initial_generated_start_utc is None:
                initial_generated_start_utc = start_date_utc
            created_count += 1

            # Prepare for the next iteration: The next period starts on the day AFTER the current one ends, at midnight.
            next_start_date_component = current_end_local_dt.date() + timedelta(days=1)
            current_start_local_dt = local_tz.localize(
                datetime.combine(next_start_date_component, time(0, 0, 0))
            )

        return created_count, initial_generated_start_utc