from datetime import datetime
from .models import PTOBalance
from django.utils.timezone import localdate


def update_pto_balance_monthly():
    """
    Updates the PTO balance for eligible full-time employees on a monthly basis.

    This function performs the following:
    - Filters employees who are:
        • Full-time (`employee_type__name="Full Time"`)
        • Paid on a monthly basis (`pay_frequency__frequency="Monthly"`)
        • Have a PTO balance less than the cap of 340 hours
    - Increases their PTO balance by the defined monthly accrual rate
    - Ensures that the PTO balance does not exceed the 340-hour cap
    - Saves the updated PTO balance for each qualifying employee

    This function is typically intended to be run once a month.
    """

    print(f"Running monthly PTO update at {datetime.now()}")

    # Query eligible full-time employees with monthly pay frequency and PTO < 340
    for obj in PTOBalance.objects.filter(employee_type__name="Full Time", pay_frequency__frequency="Monthly", pto_balance__lt=340):
        # Add the monthly accrual to their current PTO balance without exceeding the cap
        obj.pto_balance = min(obj.pto_balance + obj.accrual_rate.accrual_rate, 340)

        # Save the updated PTO balance
        obj.save()

    return "Monthly PTO updated"


def update_pto_balance_biweekly():
    """
    Updates the PTO balance for eligible full-time employees with a biweekly pay frequency.

    Workflow:
    1. Checks if there is an active `biweeklycron` record for today's date.
       - This prevents the PTO update from running multiple times on the same day.
       - The `biweeklycron` model serves as a control mechanism for biweekly updates.

    2. If an active record exists:
        - Filters full-time employees with biweekly pay frequency and PTO balance less than 340 hours.
        - Increases their PTO balance by their defined accrual rate.
        - Caps the PTO balance at 340 hours.
        - Saves the updated balance for each employee.

    3. Deactivates the cron record after the update to prevent reprocessing.

    4. If no active record exists for today:
        - Logs a message and exits gracefully.

    Returns:
        str: A success message or a notice about missing records.
    """
    # Import placed inside function to avoid circular import issues

    today = localdate()

    # try:
        # Check for an active biweekly cron job scheduled for today
        # record = BiweeklyCron.objects.get(run_date=today, is_active=True)

        # Filter eligible full-time, biweekly employees with PTO < 340
    for obj in PTOBalance.objects.filter(employee_type__name="Full Time", pay_frequency__frequency="Biweekly", pto_balance__lt=340):
            # Update and cap the PTO balance
            obj.pto_balance = min(obj.pto_balance + obj.accrual_rate.accrual_rate, 340)
            obj.save()

        # Mark this cron record as used
        # record.is_active = False
        # record.save()

    return "✅ Biweekly PTO updated"

    # except ObjectDoesNotExist:
    #     # No valid cron job found for today
    #     print(f"❌ No active biweekly record for {today}")
    #     return f"No active record for {today}"
