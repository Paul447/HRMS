from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from yearofexperience.tasks import update_experience_records
from ptobalance.tasks import update_pto_balance_monthly, update_pto_balance_biweekly

def schedule_update_experience(scheduler):
    scheduler.add_job(update_experience_records, CronTrigger(hour=22, minute=55), id='experience_update', replace_existing=True)

def schedule_update_pto_monthly(scheduler):
    scheduler.add_job(update_pto_balance_monthly, CronTrigger(day='last', hour=23, minute=50), id='pto_monthly', replace_existing=True)

def schedule_update_pto_biweekly(scheduler):
    scheduler.add_job(update_pto_balance_biweekly, CronTrigger(hour=22, minute=0), id='pto_biweekly', replace_existing=True)

def start_scheduler():
    scheduler = BackgroundScheduler(timezone='America/Chicago')
    schedule_update_experience(scheduler)
    schedule_update_pto_monthly(scheduler)
    schedule_update_pto_biweekly(scheduler)
    scheduler.start()
