# balancededuct.py


from django.core.exceptions import ValidationError
from unverifiedsickleave.models import SickLeaveBalance

# from sickpolicy.models import MaxSickValue # Assuming this is still needed elsewhere or for future use
from decimal import Decimal
from ptobalance.models import PTOBalance  # Assuming this is needed for PTO handling


# --- Helper function to get the PTO balance object ---
def get_pto_balance_object(timeoff_request_instance):
    """
    Retrieves the PTOBalance object for the employee linked to the TimeoffRequest.
    Raises ValidationError if the balance entry does not exist.
    """
    if not timeoff_request_instance.employee:
        raise ValidationError("Time off request must be associated with an employee.")

    try:
        # Access the employee through the passed timeoff_request_instance
        return PTOBalance.objects.select_for_update().get(user=timeoff_request_instance.employee)
    except PTOBalance.DoesNotExist:
        raise ValidationError(f"User '{timeoff_request_instance.employee.username}' does not have a PTO balance entry.")


# --- Helper function to get the SickLeaveBalance object ---
def get_sick_leave_balance_object(timeoff_request_instance):
    """
    Retrieves the SickLeaveBalance object for the employee linked to the TimeoffRequest.
    Raises ValidationError if the balance entry does not exist.
    """
    if not timeoff_request_instance.employee:
        raise ValidationError("Time off request must be associated with an employee.")

    try:
        # Access the employee through the passed timeoff_request_instance
        return SickLeaveBalance.objects.select_for_update().get(user=timeoff_request_instance.employee)
    except SickLeaveBalance.DoesNotExist:
        raise ValidationError(f"User '{timeoff_request_instance.employee.username}' does not have a sick leave balance entry.")


# --- Functions to deduct balances ---
def _deduct_unvsl_balance(timeoff_request_instance, hours_to_deduct):
    """
    Deducts hours from the unverified sick leave balance.
    Performs validation for non-negative deduction and sufficient balance.
    """
    if not isinstance(hours_to_deduct, (int, float, Decimal)) or hours_to_deduct < 0:
        raise ValidationError("Hours to deduct must be a non-negative number.")

    hours_to_deduct_decimal = Decimal(str(hours_to_deduct))  # Ensure Decimal type

    balance_obj = get_sick_leave_balance_object(timeoff_request_instance)  # Pass the instance here

    if balance_obj.unverified_sick_balance < hours_to_deduct_decimal:
        raise ValidationError(f"Insufficient unverified sick leave balance for user '{timeoff_request_instance.employee.username}'. " f"Required: {hours_to_deduct_decimal}, Available: {balance_obj.unverified_sick_balance}")

    balance_obj.unverified_sick_balance -= hours_to_deduct_decimal
    balance_obj.save(update_fields=["unverified_sick_balance"])
    print(f"Deducted {hours_to_deduct} UNVSL hours for {timeoff_request_instance.employee.username}. New balance: {balance_obj.unverified_sick_balance}")


def _deduct_vsl_balance(timeoff_request_instance, hours_to_deduct):
    """
    Deducts hours from the verified sick leave balance.
    Performs validation for non-negative deduction and sufficient balance.
    """
    if not isinstance(hours_to_deduct, (int, float, Decimal)) or hours_to_deduct < 0:
        raise ValidationError("Hours to deduct must be a non-negative number.")

    hours_to_deduct_decimal = Decimal(str(hours_to_deduct))  # Ensure Decimal type

    balance_obj = get_sick_leave_balance_object(timeoff_request_instance)  # Pass the instance here

    if balance_obj.verified_sick_balance < hours_to_deduct_decimal:
        raise ValidationError(f"Insufficient verified sick leave balance for user '{timeoff_request_instance.employee.username}'. " f"Required: {hours_to_deduct_decimal}, Available: {balance_obj.verified_sick_balance}")

    balance_obj.verified_sick_balance -= hours_to_deduct_decimal
    balance_obj.save(update_fields=["verified_sick_balance"])
    print(f"Deducted {hours_to_deduct} VSL/FVSL hours for {timeoff_request_instance.employee.username}. New balance: {balance_obj.verified_sick_balance}")


def _deduct_pto_balance(timeoff_request_instance, hours_to_deduct):
    """
    Deducts hours from the PTO balance.
    Performs validation for non-negative deduction and sufficient balance.
    """
    if not isinstance(hours_to_deduct, (int, float, Decimal)) or hours_to_deduct < 0:
        raise ValidationError("Hours to deduct must be a non-negative number.")

    hours_to_deduct_decimal = Decimal(str(hours_to_deduct))  # Ensure Decimal type

    balance_obj = get_pto_balance_object(timeoff_request_instance)  # Pass the instance here

    if balance_obj.pto_balance < hours_to_deduct_decimal:
        raise ValidationError(f"Insufficient PTO balance for user '{timeoff_request_instance.employee.username}'. " f"Required: {hours_to_deduct_decimal}, Available: {balance_obj.pto_balance}")

    balance_obj.pto_balance -= hours_to_deduct_decimal
    balance_obj.save(update_fields=["pto_balance"])
    print(f"Deducted {hours_to_deduct} PTO hours for {timeoff_request_instance.employee.username}. New balance: {balance_obj.pto_balance}")


# --- Main function to perform deduction based on leave type ---
def perform_balance_deduction_on_approval(timeoff_request_instance, hours_to_deduct):
    """
    Performs the appropriate sick leave balance deduction based on the leave type.
    Handles various validation checks before attempting deduction.
    """
    if not timeoff_request_instance:
        raise ValidationError("No TimeoffRequest instance provided for balance deduction.")

    if not timeoff_request_instance.requested_leave_type:
        raise ValidationError(f"Time off request (ID: {timeoff_request_instance.pk}) has no associated leave type. Cannot deduct balance.")

    # Access the name from the linked LeaveType model
    leave_type_name = timeoff_request_instance.requested_leave_type.leave_type.name

    print(f"Attempting deduction for {timeoff_request_instance.employee.username}, Leave Type: {leave_type_name}, Hours: {hours_to_deduct}")  # For debugging

    if leave_type_name == "UNVSL":
        _deduct_unvsl_balance(timeoff_request_instance, hours_to_deduct)
    elif leave_type_name in ["VSL", "FVSL"]:
        _deduct_vsl_balance(timeoff_request_instance, hours_to_deduct)
    elif leave_type_name == "PTO":
        _deduct_pto_balance(timeoff_request_instance, hours_to_deduct)
    else:
        pass
        # raise ValidationError(f"No balance deduction rule defined for leave type: '{leave_type_name}'.")
