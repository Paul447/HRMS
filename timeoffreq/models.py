import logging
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz
from datetime import datetime, timedelta, time
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .utils import pto_document_upload_path
from payperiod.models import PayPeriod

logger = logging.getLogger(__name__)

class TimeoffRequest(models.Model):
    employee = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='timeoff_requests',
        verbose_name='Employee',
    )
    requested_leave_type = models.ForeignKey(
        'leavetype.DepartmentBasedLeaveType',
        on_delete=models.CASCADE,
        related_name='timeoff_requests',
        verbose_name='Leave Type',
        help_text='Type of leave requested by the employee',
    )
    start_date_time = models.DateTimeField(
        verbose_name='Start Date and Time',
        help_text='Start date and time of the requested leave',
    )
    end_date_time = models.DateTimeField(
        verbose_name='End Date and Time',
        help_text='End date and time of the requested leave',
    )
    time_off_duration = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Time Off Duration',
        help_text='Duration in hours, automatically calculated based on start and end date/time',
    )
    employee_leave_reason = models.CharField(
        max_length=255,
        verbose_name='Leave Reason',
        help_text='Reason for the leave request'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
        verbose_name='Time off Status',
    )
    reference_pay_period = models.ForeignKey(
        'payperiod.PayPeriod',
        on_delete=models.CASCADE,
        related_name='timeoff_requests',
        verbose_name='Pay Period',
        help_text='Pay period during which the time off is requested',
    )
    medical_document_proof = models.FileField(
        upload_to=pto_document_upload_path,
        blank=True,
        null=True,
        verbose_name='Medical Document Proof',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Upload a medical document proof for applicable leave requests (only PDF, JPG, JPEG, PNG allowed)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Timestamp when the time off request was created',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Timestamp when the time off request was last updated',
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timeoff_requests',
        verbose_name='Approved By',
        help_text='User who approved the time off request'
    )
    rejected_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_timeoff_requests',
        verbose_name='Rejected By',
        help_text='User who rejected the time off request'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Approved At',
        help_text='Timestamp when the time off request was approved'
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Rejected At',
        help_text='Timestamp when the time off request was rejected'
    )

    class Meta:
        verbose_name = 'Time Off Request'
        verbose_name_plural = 'Time Off Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date_time', 'end_date_time']),
        ]

    def __str__(self):
        local_start = timezone.localtime(self.start_date_time).strftime('%a %m/%d %H:%M %p')
        local_end = timezone.localtime(self.end_date_time).strftime('%a %m/%d %H:%M %p')
        return f"{self.employee.first_name} - {self.requested_leave_type.leave_type.name} ({local_start} to {local_end})"

    def clean(self):
        """Validate the instance before saving."""
        super().clean()
        if self.start_date_time and self.end_date_time:
            if self.end_date_time <= self.start_date_time:
                raise ValidationError("End date and time must be after start date and time.")
            duration_hours = (self.end_date_time - self.start_date_time).total_seconds() / 3600.0
            if duration_hours <= 0:
                raise ValidationError("Time off request must have a positive duration.")
            if self.time_off_duration != round(duration_hours, 2):
                raise ValidationError("Time off duration does not match the period between start and end dates.")
            if self.requested_leave_type and self.requested_leave_type.leave_type.name in ['FVSL', 'VSL'] and not self.medical_document_proof:
                raise ValidationError(f"Medical document is required for {self.requested_leave_type.leave_type.name} requests.")

    def save(self, *args, **kwargs):
        """Custom save method to handle create and update logic."""
        process_timeoff_logic = kwargs.pop('process_timeoff_logic', True)
        is_new = not self.pk

        # Ensure timezone awareness
        if self.start_date_time and timezone.is_naive(self.start_date_time):
            self.start_date_time = timezone.make_aware(self.start_date_time, timezone.get_current_timezone())
        if self.end_date_time and timezone.is_naive(self.end_date_time):
            self.end_date_time = timezone.make_aware(self.end_date_time, timezone.get_current_timezone())

        # Validate before saving
        self.full_clean()

        # Store original values for comparison
        original_time_off_duration = self.time_off_duration
        original_end_date_time = self.end_date_time
        original_reference_pay_period = self.reference_pay_period

        if is_new:
            self._handle_create(process_timeoff_logic)
        else:
            self._handle_update(process_timeoff_logic, original_time_off_duration, original_end_date_time, original_reference_pay_period)

    def _handle_create(self, process_timeoff_logic):
        """Handle logic for creating a new instance."""
        # Store original values for comparison
        original_time_off_duration = self.time_off_duration
        original_end_date_time = self.end_date_time
        original_reference_pay_period = self.reference_pay_period
        original_status = self.status  # Add more fields if needed

        # Assign pay period if not set
        if not self.reference_pay_period and self.start_date_time:
            self.reference_pay_period = PayPeriod.get_pay_period_for_date(self.start_date_time)
            if not self.reference_pay_period:
                raise ValidationError(f"No PayPeriod found for {self.start_date_time}. Please ensure pay periods are configured.")

        # Perform initial save to assign PK
        super().save()

        # Process TO splitting if enabled
        if process_timeoff_logic and self.start_date_time and self.end_date_time:
            self._process_to_splitting()

        # Run custom business logic
        self.post_create_business_logic()

        # Save again only if attributes changed
        if (self.time_off_duration != original_time_off_duration or
                self.end_date_time != original_end_date_time or
                self.reference_pay_period != original_reference_pay_period or
                self.status != original_status):
            super().save(update_fields=['time_off_duration', 'end_date_time', 'reference_pay_period', 'status'])

    def _handle_update(self, process_timeoff_logic, original_time_off_duration, original_end_date_time, original_reference_pay_period):
        """Handle logic for updating an existing instance."""
        # Re-assign pay period if start_date_time changed and pay_period not set
        if not self.reference_pay_period and self.start_date_time:
            self.reference_pay_period = PayPeriod.get_pay_period_for_date(self.start_date_time)
            if not self.reference_pay_period:
                raise ValidationError(f"No PayPeriod found for {self.start_date_time}. Please ensure pay periods are configured.")

        # Perform initial save
        super().save()

        # Process TO splitting if enabled and relevant fields changed
        if process_timeoff_logic and self.start_date_time and self.end_date_time:
            self._process_to_splitting()

        # Run custom business logic
        self.post_update_business_logic()

        # Save again if attributes changed
        if (self.time_off_duration != original_time_off_duration or
                self.end_date_time != original_end_date_time or
                self.reference_pay_period != original_reference_pay_period):
            super().save(update_fields=['time_off_duration', 'end_date_time', 'reference_pay_period'], process_timeoff_logic=False)

    def post_create_business_logic(self):
        """Hook for additional business logic after creation."""
        pass  # Override in your implementation

    def post_update_business_logic(self):
        """Hook for additional business logic after update."""
        pass  # Override in your implementation

    def _process_to_splitting(self):
        """Orchestrates TO splitting logic."""
        if not self.start_date_time or not self.end_date_time:
            self.time_off_duration = 0.0
            return

        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_start = self.start_date_time.astimezone(local_tz)
        local_end = self.end_date_time.astimezone(local_tz)

        # Check for midnight crossing (daily split)
        if local_start.date() != local_end.date():
            self._split_to_across_midnight(local_start, local_end)
        else:
            # Process single-day segment for pay period assignment and splitting
            self._assign_hours_and_split_by_pay_period(local_start, local_end)

    def _split_to_across_midnight(self, local_start_time, local_original_end_time):
        """Splits a Time Off request across midnight boundaries."""
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Calculate first day's end at midnight
        first_day_end_boundary_naive = datetime.combine(local_start_time.date() + timedelta(days=1), time(0, 0, 0))
        first_day_end_boundary_local = local_tz.normalize(local_tz.localize(first_day_end_boundary_naive))

        # Update current instance for first day
        current_instance_end_local = first_day_end_boundary_local
        first_day_duration = current_instance_end_local - local_start_time
        first_day_hours = round(first_day_duration.total_seconds() / 3600.0, 2)
        self.end_date_time = current_instance_end_local.astimezone(pytz.utc)
        self.time_off_duration = first_day_hours

        # Create subsequent days' portions
        next_segment_start_local = current_instance_end_local

        while next_segment_start_local < local_original_end_time:
            daily_segment_end_boundary_naive = datetime.combine(next_segment_start_local.date() + timedelta(days=1), time(0, 0, 0))
            daily_segment_end_boundary_local = local_tz.normalize(local_tz.localize(daily_segment_end_boundary_naive))
            current_daily_segment_end_local = min(local_original_end_time, daily_segment_end_boundary_local)

            daily_segment_duration = current_daily_segment_end_local - next_segment_start_local
            daily_segment_hours = round(daily_segment_duration.total_seconds() / 3600.0, 2)

            if daily_segment_hours <= 0:
                break

            new_to_entry = TimeoffRequest(
                employee=self.employee,
                requested_leave_type=self.requested_leave_type,
                start_date_time=next_segment_start_local.astimezone(pytz.utc),
                end_date_time=current_daily_segment_end_local.astimezone(pytz.utc),
                time_off_duration=daily_segment_hours,
                employee_leave_reason=self.employee_leave_reason,
                status=self.status,
                medical_document_proof=self.medical_document_proof,
            )
            new_to_entry.save(process_timeoff_logic=True)

            next_segment_start_local = current_daily_segment_end_local

    def _assign_hours_and_split_by_pay_period(self, local_start_time, local_end_time):
        """Assigns pay period and splits if crossing pay period boundary."""
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Assign pay period
        current_pay_period = PayPeriod.get_pay_period_for_date(local_start_time)
        self.reference_pay_period = current_pay_period

        if not current_pay_period:
            self.time_off_duration = 0.0
            logger.warning(f"No PayPeriod found for {local_start_time} during Time Off details calculation.")
            return

        # Calculate pay period boundary
        pay_period_boundary_naive = datetime.combine(current_pay_period.end_date + timedelta(days=1), time(0, 0, 0))
        pay_period_boundary_local = local_tz.normalize(local_tz.localize(pay_period_boundary_naive))

        # Check for pay period crossing
        if local_end_time > pay_period_boundary_local:
            self._split_to_at_pay_period_boundary(local_start_time, local_end_time, pay_period_boundary_local)
        else:
            delta = local_end_time - local_start_time
            self.time_off_duration = round(delta.total_seconds() / 3600.0, 2)

    def _split_to_at_pay_period_boundary(self, local_start_time, local_original_end_time, pay_period_boundary_local):
        """Splits a Time Off segment at a pay period boundary."""
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Update current instance for first pay period
        first_segment_end_local = pay_period_boundary_local
        first_segment_duration = first_segment_end_local - local_start_time
        first_segment_hours = round(first_segment_duration.total_seconds() / 3600.0, 2)
        self.end_date_time = first_segment_end_local.astimezone(pytz.utc)
        self.time_off_duration = first_segment_hours

        # Create next pay period's portion
        next_segment_start_local = first_segment_end_local
        next_segment_end_local = local_original_end_time
        next_segment_duration = next_segment_end_local - next_segment_start_local
        next_segment_hours = round(next_segment_duration.total_seconds() / 3600.0, 2)

        if next_segment_hours > 0:
            subsequent_pay_period = PayPeriod.get_pay_period_for_date(next_segment_start_local)
            new_to_entry = TimeoffRequest(
                employee=self.employee,
                requested_leave_type=self.requested_leave_type,
                start_date_time=next_segment_start_local.astimezone(pytz.utc),
                end_date_time=next_segment_end_local.astimezone(pytz.utc),
                time_off_duration=next_segment_hours,
                employee_leave_reason=self.employee_leave_reason,
                status=self.status,
                reference_pay_period=subsequent_pay_period,
                medical_document_proof=self.medical_document_proof,
            )
            new_to_entry.save(process_timeoff_logic=True)
