from celery import shared_task
import logging
from .utils import unverified_verified_update
from datetime import date

logger = logging.getLogger(__name__)

@shared_task
def update_unverified_verified_sick_leave():
    """
    Task to update unverified and verified sick leave balances biweekly.
    
    This task is intended to be run biweekly to ensure that the sick leave balances are updated according to the defined policy.
    """

    logger.info("Starting unverified and verified sick leave balance update.")
    reference_date = date(2025, 6, 29)
    print(f"Reference date for biweekly update: {reference_date}")
    today = date.today()
    print(f"Today's date: {today}")
    days_since = (today - reference_date).days
    if days_since % 14 == 0:
        print(f"✅Days since reference date: {days_since}")
        logger.info(f"✅Running biweekly PTO update at {today}")
        unverified_verified_update()
        logger.info("Successfully updated unverified and verified sick leave balances.")
    else: 
        logger.error(f"Skipping sick leave update for {today} as it is not a biweekly date since {reference_date}. Days since: {days_since}")

