from django.core.exceptions import ValidationError
from decimal import Decimal
from sickpolicy.models import SickLeaveProratedValue, MaxSickValue
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


