from datetime import datetime
from .models import PTOBalance
from django.utils.timezone import localdate


def update_pto_balance_biweekly():
    """
    Updates the PTO balance for eligible full-time employees 
    with a biweekly pay frequency.

    - Finds all full-time employees with biweekly pay frequency 
      whose PTO balance is less than 340 hours.
    - Increases their PTO balance by their accrual rate, capped at 340.
    """

    employees = PTOBalance.objects.filter(
        employee_type__name="Full Time",
        pay_frequency__frequency="Biweekly",
        pto_balance__lt=340
    )

    updated_count = 0
    for emp in employees:
        if emp.accrual_rate:
            emp.pto_balance = min(emp.pto_balance + emp.accrual_rate.accrual_rate, 340)
            emp.save(update_fields=["pto_balance"])
            updated_count += 1

    return f"✅ Biweekly PTO updated for {updated_count} employees"

