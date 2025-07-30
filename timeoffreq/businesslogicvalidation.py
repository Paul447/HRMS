from django.utils import timezone
from unverifiedsickleave.models import SickLeaveBalance
from sickpolicy.models import MaxSickValue
from decimal import Decimal


def make_timezone_aware(dt, target_tz=None):
    """
    Ensures a datetime is timezone-aware, localizing naive datetimes to the target timezone.

    Args:
        dt: Datetime object (aware or naive).
        target_tz: Timezone object (defaults to current timezone).

    Returns:
        Timezone-aware datetime or None if dt is None.
    """
    if not dt:
        return None
    if not target_tz:
        target_tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, target_tz)
    return dt.astimezone(target_tz)


def validate_duration(start_date_time, end_date_time):
    """
    Validates that the time-off duration is positive and dates are provided.

    Args:
        start_date_time: Start datetime of the request.
        end_date_time: End datetime of the request.

    Returns:
        Tuple of (total_hours, errors_dict).
    """
    errors = {}
    total_hours = Decimal("0.00")

    if not start_date_time:
        errors["start_date_time"] = "Start date and time is required."
    if not end_date_time:
        errors["end_date_time"] = "End date and time is required."

    if start_date_time and end_date_time:
        if (end_date_time - start_date_time).total_seconds() <= 0:
            errors["duration"] = "Time off request must have a positive duration."
        else:
            total_hours = Decimal(str(round((end_date_time - start_date_time).total_seconds() / 3600.0, 2)))

    return total_hours, errors


def validate_medical_document(leave_type_name, medical_document):
    """
    Validates medical document requirements for specific leave types.

    Args:
        leave_type_name: Name of the leave type (e.g., 'VSL', 'FVSL').
        medical_document: Medical document file (if provided).

    Returns:
        Dictionary of errors (empty if valid).
    """
    errors = {}
    if leave_type_name in ["VSL", "FVSL"] and not medical_document:
        errors["medical_document"] = f"Medical documentation is required for {leave_type_name}."
    return errors


def validate_leave_balance(user, leave_type_name, total_hours, use_select_for_update):
    """
    Validates leave balances for the requested hours and leave type.

    Args:
        user: User instance making the request.
        leave_type_name: Name of the leave type (e.g., 'UNVSL', 'VSL', 'FVSL').
        total_hours: Total hours requested.
        use_select_for_update: If True, uses select_for_update for balance checks.

    Returns:
        Dictionary of errors (empty if valid).
    """
    errors = {}
    if total_hours <= 0 or not user or not leave_type_name:
        return errors

    try:
        query = SickLeaveBalance.objects.select_for_update() if use_select_for_update else SickLeaveBalance.objects
        balance = query.get(user=user)

        # UNVSL checks
        if leave_type_name == "UNVSL":
            if balance.unverified_sick_balance < balance.sick_prorated.prorated_unverified_sick_leave:
                errors["unverified_sick_balance"] = f"Insufficient unverified sick leave balance. Current: {balance.unverified_sick_balance} hrs, " f"Prorated Max: {balance.sick_prorated.prorated_unverified_sick_leave} hrs."
            if total_hours > balance.unverified_sick_balance:
                errors["unverified_sick_balance"] = f"Insufficient unverified sick leave. Requested: {total_hours} hrs, " f"Available: {balance.unverified_sick_balance} hrs."

        # VSL and FVSL checks for verified_sick_balance
        if leave_type_name in ["VSL", "FVSL"]:
            if total_hours > balance.verified_sick_balance:
                errors["verified_sick_balance"] = f"Insufficient verified sick leave. Requested: {total_hours} hrs, " f"Available: {balance.verified_sick_balance} hrs."

        # FVSL-specific check for used_FVSL against threshold
        if leave_type_name == "FVSL":
            max_sick_value = MaxSickValue.objects.first()
            if not max_sick_value:
                errors["max_sick_value"] = "Maximum sick leave threshold not configured."
            else:
                if balance.used_FVSL + total_hours > max_sick_value.threshold_FVSL:
                    errors["used_FVSL"] = f"Insufficient family care leave balance. Used balance: {balance.used_FVSL} hrs, " f"Max: {max_sick_value.threshold_FVSL} hrs."

    except SickLeaveBalance.DoesNotExist:
        errors["balance"] = "User does not have a sick leave balance entry."
    except Exception as e:
        errors["balance_check_error"] = f"An unexpected error occurred during balance check: {str(e)}"

    return errors


def validate_pto_request(user, leave_type, start_date_time, end_date_time, medical_document=None, instance=None, use_select_for_update=False):
    """
    Centralized validation for PTO requests, used by model.clean and serializer.validate.

    Performs soft business logic validations and returns a dictionary of errors.

    Args:
        user: User instance making the request.
        leave_type: LeaveType instance for the request.
        start_date_time: Start datetime of the PTO request.
        end_date_time: End datetime of the PTO request.
        medical_document: Medical document file (if applicable).
        instance: Existing PTORequest instance (for updates).
        use_select_for_update: If True, uses select_for_update for balance checks.

    Returns:
        Dictionary of errors (empty if valid).
    """
    errors = {}

    # Normalize datetimes
    start_date_time = make_timezone_aware(start_date_time)
    end_date_time = make_timezone_aware(end_date_time)

    # Validate duration and calculate total hours
    total_hours, duration_errors = validate_duration(start_date_time, end_date_time)
    errors.update(duration_errors)

    # Validate medical document
    leave_type_name = leave_type.name if leave_type else None
    if leave_type_name:
        errors.update(validate_medical_document(leave_type_name, medical_document))

    # Validate leave balances
    errors.update(validate_leave_balance(user, leave_type_name, total_hours, use_select_for_update))

    return errors
