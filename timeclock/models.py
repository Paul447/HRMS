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

    class Meta:
        verbose_name = "Clock Entry"
        # verbose_plural = "Clock Entries"
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
        Overrides the default save method to automate PayPeriod assignment and
        trigger hours calculation when appropriate.
        Uses a 'calculate_hours' flag to prevent infinite recursion.
        """
        # Pop the custom flag to prevent it from being passed to super().save()
        calculate_hours_flag = kwargs.pop('calculate_hours', True)

        # Ensure clock_in_time is timezone-aware if it's naive
        if self.clock_in_time and timezone.is_naive(self.clock_in_time):
            self.clock_in_time = timezone.make_aware(self.clock_in_time, timezone.get_current_timezone())

        # Assign PayPeriod if clock_in_time is set and pay_period is not yet assigned
        if self.clock_in_time and not self.pay_period:
            self.pay_period = PayPeriod.get_pay_period_for_date(self.clock_in_time)
            if not self.pay_period:
                print(f"Warning: No PayPeriod found for {self.clock_in_time}. Please create one.")

        # Store original values to check if fields actually changed after calculation
        original_hours_worked = self.hours_worked
        original_clock_out_time = self.clock_out_time

        # Perform the initial save to ensure the object has a primary key
        # and other fields are persisted.
        super().save(*args, **kwargs)

        # Calculate hours only if both clock-in and clock-out times are present
        # AND if this save call is meant to trigger calculation (not a recursive call)
        if self.clock_in_time and self.clock_out_time and calculate_hours_flag:
            self._calculate_and_assign_hours()

            # If hours_worked or clock_out_time (for split shifts) changed,
            # save again, but prevent re-calculation by setting calculate_hours_flag to False.
            if self.hours_worked != original_hours_worked or \
               self.clock_out_time != original_clock_out_time:
                # Use update_fields to save only the changed fields, improving efficiency
                self.save(update_fields=['hours_worked', 'clock_out_time'], calculate_hours=False)


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
            return # No self.save() here

        # Use the project's default timezone (e.g., 'America/Chicago') for business logic
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Convert clock times to the local timezone for accurate day/time comparisons
        local_clock_in_time = self.clock_in_time.astimezone(local_tz)
        local_clock_out_time = self.clock_out_time.astimezone(local_tz)

        # Determine if the shift spans across midnight
        spans_midnight = local_clock_in_time.date() != local_clock_out_time.date()

        if spans_midnight:
            # Handle the complex logic for splitting the shift.
            # This method will modify self.hours_worked and self.clock_out_time
            # for the current instance (first day's portion) and create a new instance
            # for the subsequent day's portion.
            self._split_shift_across_midnight(local_clock_in_time, local_clock_out_time)
        else:
            # Normal duration calculation for shifts within the same day
            delta = local_clock_out_time - local_clock_in_time
            self.hours_worked = round(delta.total_seconds() / 3600, 2)
            # No self.save() here. The changes will be saved by the calling save() method.

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
        # A robust way to get the end of the first day is to find midnight of the *next* day
        # and subtract a microsecond. Midnight (00:00:00) is generally less problematic
        # during DST transitions.
        next_day_start_naive = datetime.combine(local_clock_in_time.date() + timedelta(days=1), time(0, 0, 0))
        next_day_start_local = local_tz.normalize(local_tz.localize(next_day_start_naive))

        first_day_end_local = next_day_start_local - timedelta(microseconds=1)

        first_day_duration = first_day_end_local - local_clock_in_time
        first_day_hours = round(first_day_duration.total_seconds() / 3600, 2)

        # Update the current Clock instance to be the first day's portion
        self.clock_out_time = first_day_end_local.astimezone(pytz.utc) # Convert back to UTC for DB
        self.hours_worked = first_day_hours
        # No self.save() here. The calling save() method will handle updating.

        # --- Create Subsequent Day's Portion ---
        # The subsequent day's portion starts at 00:00:00 on the clock-out date
        subsequent_day_start_naive = datetime.combine(local_clock_out_time.date(), time(0, 0, 0))
        subsequent_day_start_local = local_tz.normalize(local_tz.localize(subsequent_day_start_naive))

        subsequent_day_duration = local_clock_out_time - subsequent_day_start_local
        subsequent_day_hours = round(subsequent_day_duration.total_seconds() / 3600, 2)

        # Get the correct PayPeriod for the subsequent day's portion
        subsequent_day_pay_period = PayPeriod.get_pay_period_for_date(subsequent_day_start_local)

        # Create a new Clock entry for the subsequent day's portion
        # Instantiate the object first, then set the flag, then save
        new_clock_entry = Clock(
            user=self.user,
            clock_in_time=subsequent_day_start_local.astimezone(pytz.utc), # Convert back to UTC
            clock_out_time=local_clock_out_time.astimezone(pytz.utc), # Convert back to UTC
            hours_worked=subsequent_day_hours,
            pay_period=subsequent_day_pay_period,
        )
        # Set the calculate_hours flag directly on the instance before saving
        new_clock_entry.calculate_hours = False
        new_clock_entry.save()
