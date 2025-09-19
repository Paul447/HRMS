# import logging
# from datetime import datetime, date
# from celery import shared_task
# from pytz import timezone
# from .utils import update_pto_balance_biweekly

# logger = logging.getLogger(__name__)

# @shared_task
# def update_pto_balance():
#     """
#     Celery task to update PTO balances for full-time employees on a biweekly schedule,
#     based on the date in the America/Chicago timezone.

#     The task calculates the number of days since a fixed reference date and
#     runs the PTO update only if today is a biweekly interval (every 14 days)
#     from that date.

#     Workflow:
#     1. Get today's date in America/Chicago timezone.
#     2. Calculate days elapsed since the reference date.
#     3. If today matches a biweekly interval, run PTO balance update.
#     4. Log the results or reasons for skipping.

#     Returns:
#         str: Status message indicating success or skip reason.
#     """
#     tz = timezone("America/Chicago")
#     today = datetime.now(tz).date()
#     reference_date = date(2025, 6, 29)
#     days_since = (today - reference_date).days
#     logger.info(f"Checking PTO update for {today} (Days since reference: {days_since}) [America/Chicago]")

#     if days_since % 14 == 0:
#         logger.info(f"Running biweekly PTO update at {today} (Days since reference: {days_since}) [America/Chicago]")
#         try:
#             result = update_pto_balance_biweekly()
#             logger.info(f"PTO update result: {result}")
#             return result
#         except Exception as e:
#             logger.error(f"Exception during PTO update at {today}: {e}", exc_info=True)
#             return f"Error during PTO update: {e}"
#     else:
#         msg = f"Skipping PTO update for {today} - not a biweekly interval since {reference_date} (Days since: {days_since}) [America/Chicago]"
#         logger.info(msg)
#         return msg


