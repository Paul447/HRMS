from django.core.exceptions import ValidationError
from decimal import Decimal
from sickpolicy.models import  MaxSickValue
from unverifiedsickleave.models import SickLeaveBalance
from logging import getLogger
from django.db import transaction


logger = getLogger(__name__)


# This method is used to update the balance of verified sick leave balance and unverified sick leave balance based on the Sick Policy intender for the cron job to run biweekly.
def unverified_verified_update():
    with transaction.atomic():
        sickleavebalances = SickLeaveBalance.objects.select_for_update().all()
        max_sick_value = MaxSickValue.objects.first()

        for sickleavebalance in sickleavebalances:
            accrual = max_sick_value.accrued_rate  # Reset accrual per user here

            max_unverified = sickleavebalance.sick_prorated.prorated_unverified_sick_leave
            if sickleavebalance.unverified_sick_balance < max_unverified:
                room = max_unverified - sickleavebalance.unverified_sick_balance
                to_add = min(room, accrual)
                sickleavebalance.unverified_sick_balance += to_add
                accrual -= to_add

            if accrual > 0:
                sickleavebalance.verified_sick_balance += accrual

            sickleavebalance.save()
            logger.info(
                f"Updated SickLeaveBalance for {sickleavebalance.user.username}: "
                f"Unverified Sick Balance: {sickleavebalance.unverified_sick_balance}, "
                f"Verified Sick Balance: {sickleavebalance.verified_sick_balance}"
            )
def reset_used_family_verified_sick_leave():
    """
    Reset the used family verified sick leave balances for all users.
    This function is intended to be at the end of year. 
    """
    try:
        sickleavebalances = SickLeaveBalance.objects.all()
        for sickleavebalance in sickleavebalances:
            sickleavebalance.used_FVSL = Decimal('0.00')
            sickleavebalance.save()
            logger.info(f"Reset used family verified sick leave for {sickleavebalance.user.username}")
    except Exception as e:
        logger.error(f"Error resetting used family verified sick leave: {e}")
        raise ValidationError("Failed to reset used family verified sick leave balances.") from e


