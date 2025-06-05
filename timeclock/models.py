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
# Make sure your 'payperiod' app is correctly configured and in INSTALLED_APPS
from payperiod.models import PayPeriod

# Assuming Holiday is defined in holiday/models.py or a similar path
# Make sure your 'holiday' app is correctly configured and in INSTALLED_APPS
from holiday.models import Holiday # <--- Import your Holiday model here

class Clock(models.Model):
    """
    Represents a single clock-in/clock-out entry for a user, with automatic
    calculation of hours worked and assignment to a pay period.
    Handles timezone conversions and splitting of shifts spanning across midnights.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Use AUTH_USER_MODEL for a more flexible user reference
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
        'payperiod.PayPeriod', # Use string reference for consistency
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

    class Meta:
        verbose_name = "Clock Entry"
        # verbose_plural = "Clock Entries" # This should be `verbose_name_plural`
        verbose_name_plural = "Clock Entries" # Corrected
        ordering = ['-clock_in_time'] # Order by most recent clock in first

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

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to automate PayPeriod assignment,
        trigger hours calculation, and determine holiday status when appropriate.
        Uses a 'calculate_hours' flag to prevent infinite recursion during split shifts.
        """
        calculate_hours_flag = kwargs.pop('calculate_hours', True)

        if self.clock_in_time and timezone.is_naive(self.clock_in_time):
            self.clock_in_time = timezone.make_aware(self.clock_in_time, timezone.get_current_timezone())

        # Assign PayPeriod
        if self.clock_in_time and not self.pay_period:
            self.pay_period = PayPeriod.get_pay_period_for_date(self.clock_in_time)
            if not self.pay_period:
                print(f"Warning: No PayPeriod found for {self.clock_in_time}. Please create one.")

        # --- Determine if it's a holiday ---
        # Only check if clock_in_time is available and if is_holiday hasn't been explicitly set
        if self.clock_in_time:
            # Convert clock_in_time to the project's local timezone for date comparison
            local_clock_in_date = timezone.localtime(self.clock_in_time).date()
            # Check if there's a Holiday entry for this date
            self.is_holiday = Holiday.objects.filter(date=local_clock_in_date).exists()
        # --- End Holiday Logic ---

        original_hours_worked = self.hours_worked
        original_clock_out_time = self.clock_out_time
        original_is_holiday = self.is_holiday # Keep track of original holiday status

        super().save(*args, **kwargs)

        if self.clock_in_time and self.clock_out_time and calculate_hours_flag:
            self._calculate_and_assign_hours()

            # Save again if hours_worked, clock_out_time, or is_holiday changed during the process
            if self.hours_worked != original_hours_worked or \
               self.clock_out_time != original_clock_out_time or \
               self.is_holiday != original_is_holiday: # Check for holiday change
                update_fields = ['hours_worked', 'clock_out_time', 'is_holiday'] # Include is_holiday
                self.save(update_fields=update_fields, calculate_hours=False)


    def _calculate_and_assign_hours(self):
        """
        Calculates hours worked for the current clock entry.
        Handles DST and splits shifts that span across midnights.
        Updates the current instance's hours_worked and potentially clock_out_time.
        IMPORTANT: This method ONLY modifies the instance attributes; it DOES NOT call self.save().
        The calling save() method is responsible for persisting these changes.
        """
        if not self.clock_in_time or not self.clock_out_time:
            self.hours_worked = None
            return

        local_tz = pytz.timezone(settings.TIME_ZONE)

        local_clock_in_time = self.clock_in_time.astimezone(local_tz)
        local_clock_out_time = self.clock_out_time.astimezone(local_tz)

        spans_midnight = local_clock_in_time.date() != local_clock_out_time.date()

        if spans_midnight:
            self._split_shift_across_midnight(local_clock_in_time, local_clock_out_time)
        else:
            delta = local_clock_out_time - local_clock_in_time
            self.hours_worked = round(delta.total_seconds() / 3600, 2)


    def _split_shift_across_midnight(self, local_clock_in_time, local_clock_out_time):
        """
        Splits a single Clock entry that spans across midnight (e.g., Tuesday 6 PM to Wednesday 6 AM).
        The current instance is modified to represent the portion on the first day.
        A new Clock instance is created for the portion on the subsequent day.
        IMPORTANT: This method ONLY modifies the current instance's attributes; it DOES NOT call self.save()
        for the current instance. It DOES create a new instance for the subsequent day's portion.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # --- Calculate First Day's Portion ---
        next_day_start_naive = datetime.combine(local_clock_in_time.date() + timedelta(days=1), time(0, 0, 0))
        next_day_start_local = local_tz.normalize(local_tz.localize(next_day_start_naive))

        first_day_end_local = next_day_start_local - timedelta(microseconds=1)

        first_day_duration = first_day_end_local - local_clock_in_time
        first_day_hours = round(first_day_duration.total_seconds() / 3600, 2)

        # Update the current Clock instance to be the first day's portion
        self.clock_out_time = first_day_end_local.astimezone(pytz.utc)
        self.hours_worked = first_day_hours
        # The `is_holiday` status for this part of the shift is determined by its clock-in date.
        # This has already been set in the main `save` method before `_calculate_and_assign_hours` was called.

        # --- Create Subsequent Day's Portion ---
        subsequent_day_start_naive = datetime.combine(local_clock_out_time.date(), time(0, 0, 0))
        subsequent_day_start_local = local_tz.normalize(local_tz.localize(subsequent_day_start_naive))

        subsequent_day_duration = local_clock_out_time - subsequent_day_start_local
        subsequent_day_hours = round(subsequent_day_duration.total_seconds() / 3600, 2)

        subsequent_day_pay_period = PayPeriod.get_pay_period_for_date(subsequent_day_start_local)

        # Determine `is_holiday` for the new entry based on its clock-in date (which is the subsequent day)
        is_subsequent_day_holiday = Holiday.objects.filter(date=subsequent_day_start_local.date()).exists()

        new_clock_entry = Clock(
            user=self.user,
            clock_in_time=subsequent_day_start_local.astimezone(pytz.utc),
            clock_out_time=local_clock_out_time.astimezone(pytz.utc),
            hours_worked=subsequent_day_hours,
            pay_period=subsequent_day_pay_period,
            is_holiday=is_subsequent_day_holiday, # Set holiday status for the new entry
        )
        new_clock_entry.save(calculate_hours=False) # Prevent re-calculation on new entry's save