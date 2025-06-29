from datetime import datetime
import logging
from django.db import transaction
from django.db.models import F
from .models import YearOfExperience
from ptobalance.models import PTOBalance
from ptobalance.admin import PTOBalanceAdmin


logger = logging.getLogger(__name__)


def update_experience_records():
    logger.info(f"Cron Job: Starting experience and PTO balance update at {datetime.now()}")

    updated_experience_count = 0
    refreshed_pto_count = 0
    total_experience_records = 0
    total_pto_records = 0

    try:
        with transaction.atomic():
            experience_records = YearOfExperience.objects.select_related("user").all()
            total_experience_records = experience_records.count()
            logger.info(f"Processing {total_experience_records} YearOfExperience records.")

            for exp in experience_records:
                new_experience = exp.calculate_experience()
                if exp.years_of_experience != new_experience:
                    exp.years_of_experience = new_experience
                    exp.save()
                    updated_experience_count += 1
                    logger.debug(f"Updated experience for user {exp.user.username} to {exp.years_of_experience} years.")

            pto_balance_records = PTOBalance.objects.select_related("user", "employee_type", "pay_frequency", "user__experience").all()
            total_pto_records = pto_balance_records.count()
            logger.info(f"Processing {total_pto_records} PTOBalance records.")

            for obj in pto_balance_records:
                try:
                    admin_instance = PTOBalanceAdmin(model=PTOBalance, admin_site=None)
                    admin_instance.save_model(request=None, obj=obj, form=None, change=True)
                    refreshed_pto_count += 1
                    logger.debug(f"Refreshed PTO balance for user {obj.user.username}.")
                except Exception as e:
                    logger.error(f"Error refreshing PTO balance for user {obj.user.username} (ID: {obj.pk}): {e}", exc_info=True)

        result_message = f"Successfully completed experience and PTO balance update. " f"Updated experience for {updated_experience_count}/{total_experience_records} users. " f"Refreshed PTO balances for {refreshed_pto_count}/{total_pto_records} users."
        logger.info(f"Cron Job: {result_message}")
        return result_message

    except Exception as e:
        logger.critical(f"Cron Job Error: An unhandled exception occurred: {e}", exc_info=True)
        return f"Error: An unhandled exception occurred: {e}"
