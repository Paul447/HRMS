from django.db import transaction
from django.db.models import F
from .models import PTOBalance


def update_pto_balance_biweekly():
    """
    Updates the PTO balance for eligible full-time employees 
    with a biweekly pay frequency.

    - Finds all full-time employees with biweekly pay frequency 
      whose PTO balance is less than 340 hours and have accrual_rate.
    - Increases their PTO balance by their accrual rate, capped at 340.
    """

    # Filter employees eligible for update
    employees = PTOBalance.objects.select_related('accrual_rate').filter(
        employee_type__name="Full Time",
        pay_frequency__frequency="Biweekly",
        pto_balance__lt=340,
        accrual_rate__isnull=False,
    )

    updated_count = 0

    with transaction.atomic():
        for emp in employees:
            increment = emp.accrual_rate.accrual_rate
            new_balance = emp.pto_balance + increment
            if new_balance > 340:
                new_balance = 340
            
            # Only update if balance actually changes to avoid unnecessary writes
            if new_balance != emp.pto_balance:
                PTOBalance.objects.filter(pk=emp.pk).update(pto_balance=new_balance)
                updated_count += 1

    return f"✅ Biweekly PTO updated for {updated_count} employees"
