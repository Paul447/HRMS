import pytz
from datetime import datetime, timedelta, time

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

# Assuming PayPeriod is defined in payperiod/models.py
from payperiod.models import PayPeriod
from leavetype.models import LeaveType  # Assuming LeaveType is defined in leavetype/models.py
# Refactor the code accordingly to the leavetype/models.py structure
# Assuming Department is defined in department/models.py
from department.models import Department
from rest_framework.response import Response



from django.contrib.auth.models import User

class PTORequests(models.Model):
    """
    Represents a Paid Time Off (PTO) request for a user.
    Automatically calculates total hours and assigns to the correct pay period(s).
    Handles requests that span multiple days (across midnights) by splitting them
    into multiple PTORequest entries, and then further splitting these daily segments
    if they span across pay period boundaries.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pto_requests',
        verbose_name="Employee"
    )
    department_name = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='pto_requests',
        verbose_name="Department"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='pto_requests',
        verbose_name="Leave Type",
        default=None,
    )
    start_date_time = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Start Date and Time",
        help_text="The exact date and time the PTO request begins (in UTC)."
    )
    end_date_time = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="End Date and Time",
        help_text="The exact date and time the PTO request ends (in UTC)."
    )
    total_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        null=True,
        blank=True,
        verbose_name="Total Hours",
        help_text="Automatically calculated total hours requested for this specific PTO entry."
    )
    reason = models.TextField(verbose_name="Reason for Request")
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending',
        verbose_name="Request Status"
    )
    pay_period = models.ForeignKey(
        'payperiod.PayPeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pto_requests',
        verbose_name="Associated Pay Period",
        help_text="The pay period to which this PTO request portion belongs. Assigned automatically."
    )
    medical_document = models.FileField(upload_to='documents/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Time off Request"
        verbose_name_plural = "Time off Requests"
        ordering = ['-start_date_time']

    def __str__(self):
        local_start = timezone.localtime(self.start_date_time).strftime('%a %m/%d %H:%M %p')
        local_end = timezone.localtime(self.end_date_time).strftime('%a %m/%d %H:%M %p')
        return f"{self.user.first_name} {self.user.last_name} (Leave Type : {self.leave_type.name}) - Time off: {local_start} to {local_end} ({self.total_hours or 0} hrs)"

    def clean(self):

        if self.start_date_time and self.end_date_time:
            if self.end_date_time < self.start_date_time:
                raise ValidationError("End date and time cannot be before start date and time.")
            if (self.end_date_time - self.start_date_time).total_seconds() <= 0:
                raise ValidationError("Time off request must have a positive duration.")

    def save(self, *args, **kwargs):
        process_pto_logic = kwargs.pop('process_pto_logic', True)

        # Ensure leave_type is loaded before accessing its name
        if self.leave_type: # Check if leave_type is set (e.g., not None)
            if self.leave_type.name == 'FVSL' and not self.medical_document:
                raise ValidationError("Medical document is required for FVSL requests.")
            if self.leave_type.name == 'VSL' and not self.medical_document:
                raise ValidationError("Medical document is required for VSL requests.")
        # Ensure times are timezone-aware
        if self.start_date_time and timezone.is_naive(self.start_date_time):
            self.start_date_time = timezone.make_aware(self.start_date_time, timezone.get_current_timezone())
        if self.end_date_time and timezone.is_naive(self.end_date_time):
            self.end_date_time = timezone.make_aware(self.end_date_time, timezone.get_current_timezone())

        # --- IMPORTANT ---
        # If this is the initial save for an object (pk is None) or if pay_period is not set yet,
        # try to assign it based on start_date_time *before* any splitting logic runs.
        # This ensures the original segment has a pay_period from the start.
        if (not self.pk or not self.pay_period) and self.start_date_time:
            self.pay_period = PayPeriod.get_pay_period_for_date(self.start_date_time)
            if not self.pay_period:
                print(f"Warning: No PayPeriod found for {self.start_date_time}. Please ensure pay periods are configured.")


        original_total_hours = self.total_hours
        original_end_date_time = self.end_date_time
        original_pay_period = self.pay_period # Store original pay_period for comparison

        # Perform the initial save. This is crucial for new objects to get a PK.
        super().save(*args, **kwargs)

        if self.start_date_time and self.end_date_time and process_pto_logic:
            self._process_pto_splitting()

            # If any attributes changed during splitting/calculation, save again
            if self.total_hours != original_total_hours or \
               self.end_date_time != original_end_date_time or \
               self.pay_period != original_pay_period: # Check pay_period change too
                fields_to_update = ['total_hours', 'end_date_time', 'pay_period']
                self.save(update_fields=fields_to_update, process_pto_logic=False)


    def _process_pto_splitting(self):
        """
        Orchestrates the PTO splitting logic.
        First, handles splitting across midnights (daily).
        Then, for each resulting daily segment, handles assigning pay period and
        further splitting if it crosses a pay period boundary.
        Updates the current instance's total_hours and potentially end_date_time.
        Creates new PTORequest instances as needed.
        """
        if not self.start_date_time or not self.end_date_time:
            self.total_hours = 0.0
            return

        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_start = self.start_date_time.astimezone(local_tz)
        local_end = self.end_date_time.astimezone(local_tz)

        # First level of splitting: Check for midnight crossing (daily split)
        if local_start.date() != local_end.date():
            self._split_pto_across_midnight(local_start, local_end)
        else:
            # If the PTO request is entirely within the same calendar day,
            # directly process it for pay period assignment and splitting
            self._assign_hours_and_split_by_pay_period(local_start, local_end)

    def _split_pto_across_midnight(self, local_start_time, local_original_end_time):
        """
        Splits a single PTORequest entry that spans across midnight (multiple calendar days).
        The current instance is modified to represent the portion on the first day.
        New PTORequest instances are created for portions on subsequent days.
        IMPORTANT: This method ONLY modifies the current instance's attributes (end_date_time, total_hours);
        it DOES NOT call self.save() for the current instance. It DOES create and save new instances
        for subsequent day's portions, allowing them to go through the full processing pipeline.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Calculate the end of the first day's portion: midnight at the start of the next day
        first_day_end_boundary_naive = datetime.combine(local_start_time.date() + timedelta(days=1), time(0, 0, 0))
        first_day_end_boundary_local = local_tz.normalize(local_tz.localize(first_day_end_boundary_naive))

        # The end time for the current instance (first day's portion) is this midnight boundary
        current_instance_end_local = first_day_end_boundary_local

        # Calculate duration for the first day's portion
        first_day_duration = current_instance_end_local - local_start_time
        first_day_hours = round(first_day_duration.total_seconds() / 3600.0, 2)

        # Update the current PTORequest instance to be the first day's portion
        self.end_date_time = current_instance_end_local.astimezone(pytz.utc)
        self.total_hours = first_day_hours
        # The pay_period for this first segment will be assigned when the calling save()
        # method re-saves this instance, and it enters _assign_hours_and_split_by_pay_period.


        # --- Create Subsequent Day's Portion(s) ---
        next_segment_start_local = current_instance_end_local # Starts at midnight of the next day

        while next_segment_start_local < local_original_end_time:
            # Determine the end of this *next* daily segment.
            # It's either the original end time OR the midnight of the day *after* this segment's start.
            daily_segment_end_boundary_naive = datetime.combine(next_segment_start_local.date() + timedelta(days=1), time(0, 0, 0))
            daily_segment_end_boundary_local = local_tz.normalize(local_tz.localize(daily_segment_end_boundary_naive))

            current_daily_segment_end_local = min(local_original_end_time, daily_segment_end_boundary_local)

            daily_segment_duration = current_daily_segment_end_local - next_segment_start_local
            daily_segment_hours = round(daily_segment_duration.total_seconds() / 3600.0, 2)

            if daily_segment_hours <= 0:
                break # Avoid creating zero-duration PTOs, or infinite loop

            # Create a new PTORequest entry for this daily segment
            new_pto_entry = PTORequests(
                user=self.user,
                department_name=self.department_name,
                leave_type=self.leave_type,
                start_date_time=next_segment_start_local.astimezone(pytz.utc),
                end_date_time=current_daily_segment_end_local.astimezone(pytz.utc),
                total_hours=daily_segment_hours,
                reason=self.reason,
                status=self.status,
                # pay_period is NOT set here; it will be assigned automatically when this new instance saves
            )
            # Crucially, allow this new instance to run the full _process_pto_splitting logic.
            # Its save() will call _process_pto_splitting(), which will then route to
            # _assign_hours_and_split_by_pay_period() for pay period assignment and further splitting if needed.
            new_pto_entry.save(process_pto_logic=True)

            # Move to the start of the next potential daily segment
            next_segment_start_local = current_daily_segment_end_local


    def _assign_hours_and_split_by_pay_period(self, local_start_time, local_end_time):
        """
        Assigns the pay period and calculates hours for a PTO segment that is confined
        to a single calendar day. This segment itself might still cross a pay period boundary.
        Updates the current instance's total_hours and potentially end_date_time.
        Creates new PTORequest instances as needed.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Assign the pay period for this segment based on its start time.
        # This explicitly ensures the pay_period is set for the current instance.
        current_pay_period = PayPeriod.get_pay_period_for_date(local_start_time)
        self.pay_period = current_pay_period # Assign it to the current instance

        if not current_pay_period:
            self.total_hours = 0.0
            print(f"Error: No PayPeriod found for {local_start_time} during PTO details calculation.")
            return

        # Determine the effective end of the current pay period for comparison.
        # This is the exact moment the next day after the pay period's end_date begins.
        pay_period_boundary_naive = datetime.combine(current_pay_period.end_date + timedelta(days=1), time(0, 0, 0))
        pay_period_boundary_local = local_tz.normalize(local_tz.localize(pay_period_boundary_naive))


        # Check if this single-day PTO segment extends beyond the current pay period's end
        spans_multiple_pay_periods = local_end_time > pay_period_boundary_local

        if spans_multiple_pay_periods:
            # The PTO segment needs to be split at the pay period boundary.
            self._split_pto_at_pay_period_boundary(local_start_time, local_end_time, pay_period_boundary_local)
        else:
            # This daily segment is entirely within its assigned pay period.
            delta = local_end_time - local_start_time
            self.total_hours = round(delta.total_seconds() / 3600.0, 2)
            # No self.save() here. The changes will be saved by the calling save() method.

    def _split_pto_at_pay_period_boundary(self, local_start_time, local_original_end_time, pay_period_boundary_local):
        """
        Splits a PTORequest segment that crosses a pay period boundary.
        The current instance is modified to represent the portion within its initial pay period.
        A new PTORequest instance is created for the portion falling into the next pay period.
        IMPORTANT: This method ONLY modifies the current instance's attributes; it DOES NOT call self.save()
        for the current instance. It DOES create and save a new instance for the subsequent pay period portion,
        allowing it to go through the full processing pipeline.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # --- Calculate First Pay Period's Portion ---
        # The end of the first segment is the pay period boundary
        first_segment_end_local = pay_period_boundary_local

        first_segment_duration = first_segment_end_local - local_start_time
        first_segment_hours = round(first_segment_duration.total_seconds() / 3600.0, 2)

        # Update the current PTORequest instance to be the first pay period's portion
        self.end_date_time = first_segment_end_local.astimezone(pytz.utc)
        self.total_hours = first_segment_hours
        # Pay period for self is already set by _assign_hours_and_split_by_pay_period.

        # --- Create Subsequent Pay Period's Portion ---
        # This new segment starts where the previous one ended.
        next_segment_start_local = first_segment_end_local

        # The end of this new segment is the original end time.
        next_segment_end_local = local_original_end_time

        next_segment_duration = next_segment_end_local - next_segment_start_local
        next_segment_hours = round(next_segment_duration.total_seconds() / 3600.0, 2)

        if next_segment_hours > 0: # Only create if there's actual duration
            # Get the correct PayPeriod for the subsequent segment based on its new start time
            subsequent_pay_period = PayPeriod.get_pay_period_for_date(next_segment_start_local)

            new_pto_entry = PTORequests(
                user=self.user,
                department_name=self.department_name,
                leave_type=self.leave_type,
                start_date_time=next_segment_start_local.astimezone(pytz.utc),
                end_date_time=next_segment_end_local.astimezone(pytz.utc),
                total_hours=next_segment_hours,
                reason=self.reason,
                status=self.status,
                pay_period=subsequent_pay_period, # Explicitly set the pay period for the new entry
            )
            # Allow this new instance to run the full _process_pto_splitting logic.
            new_pto_entry.save(process_pto_logic=True)