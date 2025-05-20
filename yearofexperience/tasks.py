from datetime import datetime
from .models import YearOfExperience
from ptobalance.models import PTOBalance
from ptobalance.admin import PTOBalanceAdmin

def update_experience_records():
    """
    Updates the 'years_of_experience' field for all users and refreshes 
    the PTO (Paid Time Off) balance accordingly.

    This function performs two main tasks:
    1. Iterates over all instances of YearOfExperience and updates each 
       instance's 'years_of_experience' value using the custom 
       'calculate_experience()' method, then saves the updated instance.

    2. Iterates over all PTOBalance instances and triggers the update logic 
       defined within the PTOBalanceAdmin class (from admin.py). This ensures 
       that PTO balances are recalculated based on the latest experience data.

    Note:
    - The PTO balance update is handled via the admin class to reuse existing 
      logic already defined in the Django admin interface.
    - This function may be scheduled to run periodically (e.g., in the evening) 
      to reflect timely updates in employee experience and PTO entitlements.
    """

    print(f"Updating experience at {datetime.now()}")

    # Update experience for all users
    for exp in YearOfExperience.objects.all():
        exp.years_of_experience = exp.calculate_experience()
        exp.save()

    # Refresh PTO balances based on updated experience
    for obj in PTOBalance.objects.all():
        admin_instance = PTOBalanceAdmin(model=PTOBalance, admin_site=None)
        admin_instance.save_model(request=None, obj=obj, form=None, change=True)

    return f"Updated experience for {YearOfExperience.objects.count()} users"
