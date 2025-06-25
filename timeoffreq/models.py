import logging
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import pytz
from datetime import datetime, timedelta, time
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .utils import pto_document_upload_path
from decimal import Decimal
from payperiod.models import PayPeriod # Assuming this model exists and works as expected
from .balancededuct import perform_balance_deduction_on_approval
from .notification import notification_and_email_trigger  
 # Assuming this function exists and works as expected   

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
        default=0.0,
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
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='timeoff_requests',
        verbose_name='Pay Period',
        help_text='Pay period during which the time off is requested',
    )
    document_proof = models.FileField( # Renamed from medical_document_proof
        upload_to=pto_document_upload_path,
        blank=True,
        null=True,
        verbose_name='Document Proof', # Verbose name updated
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Upload a document proof for applicable leave requests (only PDF, JPG, JPEG, PNG allowed)' # Help text updated
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
    reviewer = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_timeoff_requests',
        verbose_name='Reviewed By',
        help_text='User who last reviewed (approved or rejected) the time off request'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Reviewed At',
        help_text='Timestamp when the time off request was last reviewed (approved or rejected)'
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
            duration_seconds = (self.end_date_time - self.start_date_time).total_seconds()
            if duration_seconds <= 0:
                raise ValidationError("Time off request must have a positive duration.")
            # Updated to use 'document_proof'
            if self.requested_leave_type and self.requested_leave_type.leave_type.name in ['FVSL', 'VSL'] and not self.document_proof:
                raise ValidationError(f"Document proof is required for {self.requested_leave_type.leave_type.name} requests.")

    def calculate_duration(self, start_dt, end_dt):
        """Calculates duration in hours, rounded to 2 decimal places."""
        if not start_dt or not end_dt:
            return Decimal('0.00')
        delta = end_dt - start_dt
        hours = delta.total_seconds() / 3600.0
        return Decimal(str(round(hours, 2)))

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
        self.full_clean() # Calls clean() which includes the duration check

        # Store original values for comparison if updating
        original_start_date_time = None
        original_end_date_time = None
        original_status = None
        if not is_new:
            try:
                original_instance = TimeoffRequest.objects.get(pk=self.pk)
                original_start_date_time = original_instance.start_date_time
                original_end_date_time = original_instance.end_date_time
                original_status = original_instance.status
            except TimeoffRequest.DoesNotExist:
                # Should not happen if self.pk exists, but good for robustness
                pass

        if not self.reference_pay_period and self.start_date_time:
            self.reference_pay_period = PayPeriod.get_pay_period_for_date(self.start_date_time)
            if not self.reference_pay_period:
                raise ValidationError(f"No PayPeriod found for {self.start_date_time}. Please ensure pay periods are configured.")

        # Calculate time_off_duration before initial save for current instance
        # This will be adjusted during splitting if applicable
        self.time_off_duration = self.calculate_duration(self.start_date_time, self.end_date_time)

        # Use a transaction to ensure atomicity for splitting operations
        with transaction.atomic():
            super().save(*args, **kwargs) # Initial save to get PK for new instances

            if process_timeoff_logic and self.start_date_time and self.end_date_time:
                # Only re-process splitting if start/end times have changed or it's a new instance
                if is_new or (original_start_date_time != self.start_date_time or original_end_date_time != self.end_date_time):
                    # The _process_to_splitting method will modify the current instance and create new ones.
                    # It relies on the instance having a PK, so it must be saved once before this.
                    # It will also implicitly handle the time_off_duration for the current instance.
                    self._process_to_splitting()
                    
                    # After splitting, if the current instance's end_date_time or duration was adjusted,
                    # save it again. Use update_fields to prevent re-triggering this save logic.
                    if original_end_date_time != self.end_date_time or self.calculate_duration(self.start_date_time, self.end_date_time) != self.time_off_duration:
                        super().save(update_fields=['end_date_time', 'time_off_duration', 'reference_pay_period'])

            if is_new:
                # If this is a new instance, we can perform any initial business logic
                self.post_save_hook(self,original_status=None)
            if not is_new:
                self.post_update_business_logic(original_status) # Pass original_status for comparison
    
    def post_save_hook(self, created, **kwargs):
        """Hook for additional notifications or actions after save."""
        if created:
            notification_and_email_trigger(self)
            pass
        else:
            # If this is an update, handle accordingly
            pass

    def post_update_business_logic(self, original_status):
        """Hook for additional business logic after update."""
        # Example: if status changes from pending to approved/rejected, update reviewer and reviewed_at
        if original_status == 'pending' and self.status in ['approved']:
            perform_balance_deduction_on_approval(self, self.time_off_duration)  # Deduct balance on approval

    def _process_to_splitting(self):
        """Orchestrates TO splitting logic."""
        if not self.start_date_time or not self.end_date_time:
            self.time_off_duration = 0.0
            return

        local_tz = pytz.timezone(settings.TIME_ZONE)
        local_start = self.start_date_time.astimezone(local_tz)
        local_end = self.end_date_time.astimezone(local_tz)

        # If the request is for multiple days, split across midnight
        if local_start.date() != local_end.date():
            self._split_to_across_midnight(local_start, local_end)
        else:
            # For single-day requests, assign pay period and handle pay period splitting
            self._assign_hours_and_split_by_pay_period(local_start, local_end)

    def _split_to_across_midnight(self, local_start_time, local_original_end_time):
        """Splits a Time Off request across midnight boundaries.
           The current instance will be updated to represent the first day's segment.
           New instances will be created for subsequent days.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)
        current_segment_start = local_start_time

        # Update the current instance for the first day's portion
        # Calculate the end of the current day (midnight of the next day)
        first_day_end_boundary_naive = datetime.combine(current_segment_start.date() + timedelta(days=1), time(0, 0, 0))
        first_day_end_boundary_local = local_tz.normalize(local_tz.localize(first_day_end_boundary_naive))
        
        # The end of the first segment is either the original end time or midnight
        current_instance_end_local = min(local_original_end_time, first_day_end_boundary_local)

        # Update the current instance's attributes
        self.end_date_time = current_instance_end_local.astimezone(pytz.utc)
        self.time_off_duration = self.calculate_duration(current_segment_start, current_instance_end_local)
        
        # Re-assign pay period for the (potentially changed) start_date_time
        self.reference_pay_period = PayPeriod.get_pay_period_for_date(current_segment_start)
        if not self.reference_pay_period:
            logger.error(f"No PayPeriod found for {current_segment_start} during midnight splitting for existing TO request {self.pk}.")
            # Decide how to handle: raise error, default to None, etc. For now, continuing.

        # If the original request extended beyond the first day, create new segments
        next_segment_start_local = current_instance_end_local
        while next_segment_start_local < local_original_end_time:
            # Determine the end of the current daily segment (midnight of next day)
            daily_segment_end_boundary_naive = datetime.combine(next_segment_start_local.date() + timedelta(days=1), time(0, 0, 0))
            daily_segment_end_boundary_local = local_tz.normalize(local_tz.localize(daily_segment_end_boundary_naive))
            
            # The end of this segment is either the original end time or the next midnight
            current_daily_segment_end_local = min(local_original_end_time, daily_segment_end_boundary_local)

            daily_segment_hours = self.calculate_duration(next_segment_start_local, current_daily_segment_end_local)

            if daily_segment_hours > 0: # Only create new entries for positive durations
                subsequent_pay_period = PayPeriod.get_pay_period_for_date(next_segment_start_local)
                if not subsequent_pay_period:
                    logger.error(f"No PayPeriod found for {next_segment_start_local} when creating split TO segment.")
                    # If a pay period is crucial, you might raise a ValidationError here
                    # For now, we'll continue, but the reference_pay_period will be None.

                new_to_entry = TimeoffRequest(
                    employee=self.employee,
                    requested_leave_type=self.requested_leave_type,
                    start_date_time=next_segment_start_local.astimezone(pytz.utc),
                    end_date_time=current_daily_segment_end_local.astimezone(pytz.utc),
                    time_off_duration=daily_segment_hours,
                    employee_leave_reason=self.employee_leave_reason,
                    status=self.status,
                    reference_pay_period=subsequent_pay_period,
                    document_proof=self.document_proof, # Updated
                    reviewer=None, 
                    reviewed_at=None,
                )
                # Pass process_timeoff_logic=False to prevent further splitting on this new segment's save
                # as it has already been determined to be a daily segment.
                new_to_entry.save(process_timeoff_logic=False)

            next_segment_start_local = current_daily_segment_end_local

    def _assign_hours_and_split_by_pay_period(self, local_start_time, local_end_time):
        """Assigns pay period and splits if crossing pay period boundary."""
        local_tz = pytz.timezone(settings.TIME_ZONE)

        current_pay_period = PayPeriod.get_pay_period_for_date(local_start_time)
        self.reference_pay_period = current_pay_period

        if not current_pay_period:
            self.time_off_duration = 0.0
            logger.warning(f"No PayPeriod found for {local_start_time} during Time Off details calculation. Duration set to 0.")
            return

        # Calculate pay period boundary (midnight of the day after pay period end)
        pay_period_boundary_naive = datetime.combine(current_pay_period.end_date + timedelta(days=1), time(0, 0, 0))
        pay_period_boundary_local = local_tz.normalize(local_tz.localize(pay_period_boundary_naive))

        # Check if the time off crosses into the next pay period
        if local_end_time > pay_period_boundary_local:
            # Split the current instance at the pay period boundary
            # The current instance will keep the portion within its pay period
            self._split_to_at_pay_period_boundary(local_start_time, local_end_time, pay_period_boundary_local)
        else:
            # If not crossing, simply calculate and set duration for the current instance
            self.time_off_duration = self.calculate_duration(local_start_time, local_end_time)


    def _split_to_at_pay_period_boundary(self, local_start_time, local_original_end_time, pay_period_boundary_local):
        """Splits a Time Off segment at a pay period boundary.
           The current instance will be updated to represent the first pay period's segment.
           A new instance will be created for the subsequent pay period's segment.
        """
        local_tz = pytz.timezone(settings.TIME_ZONE)

        # Determine the end of the current instance's segment (at the pay period boundary)
        first_segment_end_local = pay_period_boundary_local
        
        # Update current instance for the first pay period's portion
        self.end_date_time = first_segment_end_local.astimezone(pytz.utc)
        self.time_off_duration = self.calculate_duration(local_start_time, first_segment_end_local)

        # Create next pay period's portion
        next_segment_start_local = first_segment_end_local
        next_segment_end_local = local_original_end_time
        
        next_segment_hours = self.calculate_duration(next_segment_start_local, next_segment_end_local)

        if next_segment_hours > 0: # Only create new entries for positive durations
            subsequent_pay_period = PayPeriod.get_pay_period_for_date(next_segment_start_local)
            if not subsequent_pay_period:
                logger.error(f"No PayPeriod found for {next_segment_start_local} when creating split TO segment at pay period boundary.")
                raise ValidationError(f"Cannot split time off: No PayPeriod found for {next_segment_start_local}.")

            new_to_entry = TimeoffRequest(
                employee=self.employee,
                requested_leave_type=self.requested_leave_type,
                start_date_time=next_segment_start_local.astimezone(pytz.utc),
                end_date_time=next_segment_end_local.astimezone(pytz.utc),
                time_off_duration=next_segment_hours,
                employee_leave_reason=self.employee_leave_reason,
                status=self.status,
                reference_pay_period=subsequent_pay_period,
                document_proof=self.document_proof, # Updated
                reviewer=None,
                reviewed_at=None,
            )
            # Pass process_timeoff_logic=False to prevent further splitting on this new segment's save.
            # It's already been determined as a segment within a pay period (or end of it).
            new_to_entry.save(process_timeoff_logic=False)