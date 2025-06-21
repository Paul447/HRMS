from django.utils import timezone
from django.core.exceptions import ValidationError
from unverifiedsickleave.models import SickLeaveBalance


def _get_sick_leave_balance_object(self):
    try:
        return SickLeaveBalance.objects.select_for_update().get(user=self.user)
    except SickLeaveBalance.DoesNotExist:
        raise ValidationError("User does not have a sick leave balance entry.")
def _deduct_unvsl_balance(self, hours_to_deduct):
    balance_obj = self._get_sick_leave_balance_object()
    balance_obj.unverified_sick_balance -= hours_to_deduct
    balance_obj.save(update_fields=['unverified_sick_balance'])

def _deduct_vsl_balance(self, hours_to_deduct):
    balance_obj = self._get_sick_leave_balance_object()
    balance_obj.verified_sick_balance -= hours_to_deduct
    balance_obj.save(update_fields=['verified_sick_balance'])

def _perform_balance_deduction_on_approval(self, hours_to_deduct):
    leave_type_name = self.leave_type.name if self.leave_type else None
    if leave_type_name == 'UNVSL':
            self._deduct_unvsl_balance(hours_to_deduct)
    elif leave_type_name in ['VSL', 'FVSL']:
        self._deduct_vsl_balance(hours_to_deduct)

def validate_pto_request(user, leave_type, start_date_time, end_date_time, medical_document=None, instance=None, use_select_for_update=False):
    """
    Centralized validation for PTO requests. Used by both model.clean and serializer.validate.
    This function performs "soft" business logic validations and returns a dictionary of errors.
    It does NOT raise exceptions.

    Args:
        user: The User instance making the request.
        leave_type: The LeaveType instance for the request.
        start_date_time: The start datetime of the PTO request.
        end_date_time: The end datetime of the PTO request.
        medical_document: The medical document file (if applicable).
        instance: The existing PTORequest instance if this is an update operation.
        use_select_for_update: If True, uses select_for_update for balance checks (for balance deductions).
                               This should typically be False for pure validation and True during the save process.

    Returns:
        A dictionary of errors if any, else an empty dict.
    """
    errors = {}
    
    # Ensure timezone awareness - important for consistent date arithmetic
    # (Though serializer handles this, it's good defensive programming here too)
    if start_date_time and timezone.is_naive(start_date_time):
        start_date_time = timezone.make_aware(start_date_time, timezone.get_current_timezone())
    if end_date_time and timezone.is_naive(end_date_time):
        end_date_time = timezone.make_aware(end_date_time, timezone.get_current_timezone())
    
    # Validate duration only if both dates are present and in a valid range.
    # The 'end_date_time < start_date_time' check is now primarily handled as a HARD validation in the serializer.
    if start_date_time and end_date_time:
        if (end_date_time - start_date_time).total_seconds() <= 0:
            errors['duration'] = "Time off request must have a positive duration."
    
    # Calculate total hours - only proceed if basic date range is valid or no errors so far
    total_hours = 0.0
    if start_date_time and end_date_time and 'duration' not in errors:
        total_hours = round((end_date_time - start_date_time).total_seconds() / 3600.0, 2)
    elif not start_date_time or not end_date_time:
        # If one is missing, total_hours can't be calculated accurately for a full period
        # Decide if you want to add a soft error here too, e.g., for incomplete range
        if not start_date_time:
            errors['start_date_time'] = "Start date and time is required."
        if not end_date_time:
            errors['end_date_time'] = "End date and time is required."
    
    # Validate medical document requirement
    leave_type_name = leave_type.name if leave_type else None
    if leave_type_name in ['VSL', 'FVSL'] and not medical_document:
        errors['medical_document'] = f"Medical documentation is required for {leave_type_name}."
    
    # Validate leave balances - only if total_hours is positive and valid for balance check
    if total_hours > 0 and user and leave_type_name:
        try:
            # Use select_for_update if this function is called during a transactional save
            query = SickLeaveBalance.objects.select_for_update() if use_select_for_update else SickLeaveBalance.objects
            balance_obj = query.get(user=user)

            # UNVSL specific checks
            if leave_type_name == 'UNVSL':
                # Check against prorated max for unverified
                if balance_obj.unverified_sick_balance < balance_obj.sick_prorated.prorated_unverified_sick_leave:
                    errors['unverified_sick_balance'] = (
                        f"Insufficient unverified sick leave balance. Current: {balance_obj.unverified_sick_balance} hrs, "
                        f"Prorated Max: {balance_obj.sick_prorated.prorated_unverified_sick_leave} hrs."
                    )
                # Check if requested hours exceed current available unverified balance
                if total_hours > balance_obj.unverified_sick_balance:
                    errors['unverified_sick_balance'] = (
                        f"Insufficient unverified sick leave. Requested: {total_hours} hrs, "
                        f"Available: {balance_obj.unverified_sick_balance} hrs."
                    )
            # VSL/FVSL specific checks
            elif leave_type_name in ['VSL', 'FVSL']:
                if total_hours > balance_obj.verified_sick_balance:
                    errors['verified_sick_balance'] = (
                        f"Insufficient verified sick leave. Requested: {total_hours} hrs, "
                        f"Available: {balance_obj.verified_sick_balance} hrs."
                    )
        except SickLeaveBalance.DoesNotExist:
            errors['balance'] = "User does not have a sick leave balance entry."
        except Exception as e:
            # Catch any other unexpected errors during balance check
            errors['balance_check_error'] = f"An unexpected error occurred during balance check: {e}"
    elif total_hours == 0 and ('start_date_time' not in errors and 'end_date_time' not in errors and 'duration' not in errors):
        # If total_hours is 0 but no duration error, it means dates were valid but resulted in 0 hours (e.g., same start/end, but that should be caught by duration)
        # Or, it could mean start/end dates were not provided, which is now handled above.
        # This branch might indicate a logical gap if 0 hours is truly invalid.
        pass # Or add a warning if 0 hours is not allowed for any PTO type.
    
    return errors