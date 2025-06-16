import pytz
from datetime import datetime, timedelta, time

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from django.db.models.functions import Cast
from django.db.models import DateField

# Assuming PayPeriod is defined in payperiod/models.py
from payperiod.models import PayPeriod

# Assuming Holiday is defined in holiday/models.py or a similar path
from holiday.models import Holiday

class Clock(models.Model):
    """
    Represents a single clock-in/clock-out entry for a user, with automatic
    calculation of hours worked and assignment to a pay period.
    Handles timezone conversions and splitting of shifts spanning across midnights.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clocks',
        verbose_name="Employee"
    )
    clock_in_time = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Clock In Time",
        help_text="The exact date and time the user clocked in (in UTC)."
    )
    clock_out_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Clock Out Time",
        help_text="The exact date and time the user clocked out (in UTC). Can be empty if still clocked in."
    )
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Hours Worked",
        help_text="Automatically calculated total hours worked for this entry."
    )
    pay_period = models.ForeignKey(
        'payperiod.PayPeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clocks',
        verbose_name="Associated Pay Period",
        help_text="The pay period to which this clock entry belongs. Assigned automatically."
    )
    is_holiday = models.BooleanField(
        default=False,
        verbose_name="Is Holiday",
        help_text="Indicates if this clock entry is for a holiday. Used for special handling."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The date and time when this clock entry was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The date and time when this clock entry was last updated."
    )

    class Meta:
        verbose_name = "Clock Entry"
        verbose_name_plural = "Clock Entries"
        ordering = ['-clock_in_time']

    def __str__(self):
        """
        Returns a string representation of the clock entry, showing user and times.
        Times are displayed in the project's local timezone.
        """
        local_clock_in = timezone.localtime(self.clock_in_time).strftime('%Y-%m-%d %H:%M')
        local_clock_out = timezone.localtime(self.clock_out_time).strftime('%H:%M') if self.clock_out_time else 'N/A'
        return f"{self.user.username} - {local_clock_in} to {local_clock_out}"

    def clean(self):
        """
        Performs model-level validation before saving.
        Ensures clock_out_time is not before clock_in_time.
        """
        if self.clock_in_time and self.clock_out_time and self.clock_out_time < self.clock_in_time:
            raise ValidationError("Clock out time cannot be before clock in time.")

    # --- New Helper Methods for Modularity ---

    def _ensure_timezone_aware(self):
        """Ensures clock_in_time is timezone-aware."""
        if self.clock_in_time and timezone.is_naive(self.clock_in_time):
            self.clock_in_time = timezone.make_aware(self.clock_in_time, timezone.get_current_timezone())

    def _assign_pay_period(self):
        """Assigns the correct PayPeriod based on clock_in_time."""
        if self.clock_in_time and not self.pay_period:
            self.pay_period = PayPeriod.get_pay_period_for_date(self.clock_in_time)
            if not self.pay_period:
                print(f"Warning: No PayPeriod found for {self.clock_in_time}. Please create one.")

    def _determine_holiday_status(self):
        """Determines if the clock entry's clock_in_time falls on a holiday."""
        if self.clock_in_time:
            local_clock_in_date = timezone.localtime(self.clock_in_time).date()
            self.is_holiday = Holiday.objects.filter(date=local_clock_in_date).exists()

    def _calculate_simple_hours(self, local_start, local_end):
        """Calculates hours for a shift within the same day."""
        delta = local_end - local_start
        return round(delta.total_seconds() / 3600, 2)

    def _handle_split_shift(self, local_clock_in_time, local_clock_out_time):
        """
        Splits a single Clock entry that spans across midnight.
        Modifies current instance for the first day and creates a new one for the next.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # First Day's Portion (modifies current self)
        next_day_start_naive = datetime.combine(local_clock_in_time.date() + timedelta(days=1), time(0, 0, 0))
        next_day_start_local = local_tz.normalize(local_tz.localize(next_day_start_naive))
        first_day_end_local = next_day_start_local - timedelta(microseconds=1)

        self.clock_out_time = first_day_end_local.astimezone(pytz.utc)
        self.hours_worked = self._calculate_simple_hours(local_clock_in_time, first_day_end_local)

        # Subsequent Day's Portion (creates new Clock instance)
        subsequent_day_start_naive = datetime.combine(local_clock_out_time.date(), time(0, 0, 0))
        subsequent_day_start_local = local_tz.normalize(local_tz.localize(subsequent_day_start_naive))

        subsequent_day_pay_period = PayPeriod.get_pay_period_for_date(subsequent_day_start_local)
        is_subsequent_day_holiday = Holiday.objects.filter(date=subsequent_day_start_local.date()).exists()

        new_clock_entry = Clock(
            user=self.user,
            clock_in_time=subsequent_day_start_local.astimezone(pytz.utc),
            clock_out_time=local_clock_out_time.astimezone(pytz.utc),
            hours_worked=self._calculate_simple_hours(subsequent_day_start_local, local_clock_out_time),
            pay_period=subsequent_day_pay_period,
            is_holiday=is_subsequent_day_holiday,
        )
        new_clock_entry.save(calculate_hours=False) # Prevent re-calculation on new entry's save

    def _process_hours_calculation(self):
        """
        Centralizes the logic for calculating hours, handling timezone conversions
        and triggering split shift logic if necessary.
        """
        if not self.clock_in_time or not self.clock_out_time:
            self.hours_worked = None
            return

        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_clock_in_time = self.clock_in_time.astimezone(local_tz)
        local_clock_out_time = self.clock_out_time.astimezone(local_tz)

        spans_midnight = local_clock_in_time.date() != local_clock_out_time.date()

        if spans_midnight:
            self._handle_split_shift(local_clock_in_time, local_clock_out_time)
        else:
            self.hours_worked = self._calculate_simple_hours(local_clock_in_time, local_clock_out_time)

    # --- Overridden Save Method ---

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to orchestrate the assignment of
        pay periods, holiday status, and hours calculation.
        """
        # Pop the custom flag to prevent it from being passed to super().save()
        calculate_hours_flag = kwargs.pop('calculate_hours', True)

        # 1. Prepare/Set Initial Attributes
        self._ensure_timezone_aware()
        self._assign_pay_period()
        self._determine_holiday_status()

        # Store original values to check if fields actually changed after potential calculation
        original_hours_worked = self.hours_worked
        original_clock_out_time = self.clock_out_time
        original_is_holiday = self.is_holiday

        # 2. Perform the initial save to ensure the object has a primary key
        # and other fields are persisted before potentially creating new objects.
        super().save(*args, **kwargs)

        # 3. Calculate Hours if appropriate (and not a recursive call)
        if self.clock_in_time and self.clock_out_time and calculate_hours_flag:
            self._process_hours_calculation()

            # 4. Save again if any derived fields changed during processing
            if self.hours_worked != original_hours_worked or \
               self.clock_out_time != original_clock_out_time or \
               self.is_holiday != original_is_holiday:
                # Use update_fields to save only the changed fields, improving efficiency
                self.save(update_fields=['hours_worked', 'clock_out_time', 'is_holiday'], calculate_hours=False)