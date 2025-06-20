from django.db import models
from django.contrib.auth.models import User
from sickpolicy.models import SickPolicy

# Create your models here.


# On the basis of the accural rate, the sick leave balance will be updated using the cron job defined in this application,
# The Unverified Sick Leave Balance will be updated first to the maximum limit only then the Verified Sick Leave Balance will be updated.
# When updating the Verified Sick Leaves with the Accural Rate, the unverified sick leave must be checked first to ensure that it is at it's maximum limit.
# Create the automatic biweekly corn job to update the Sick Leave Balance based on the accrual rate.
class SickLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sick_leave_balance")
    sick_policy = models.ForeignKey(SickPolicy, on_delete=models.CASCADE, related_name="sick_leave_balances")  # Link to the SickPolicy model
    unverified_sick_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Unverified sick leave balance field
    verified_sick_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Verified sick leave balance field
    verified_family_care_balance = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0,
        help_text="Verified family care leave balance, maximum 96 hours per employee per year, not prorated by FTE."
    ) # Verified family care leave balance field track the balance 96hr maximum limit per year, not prorated by FTE. Reset to 0 at the end of the year
    is_new_hire = models.BooleanField(default=False, help_text="Indicates if the user is a new hire. If True, the verified sick leave balance will be initialized with the upfront verified sick leave from the SickPolicy.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    # This method is used to validate the unverified sick leave with the Sick Policy Semo maximum unverified sick leave.
    def validate_unverified_sick_balance(self):
        if self.sick_policy.fte_value < 0.5:
            raise ValueError("FTE must be greater than or equal to 0.5 as per SEMO policy.")
        max_unverified = self.sick_policy.max_unverified_sick_leave
        if self.unverified_sick_balance > max_unverified:
            raise ValueError(f"Unverified sick leave balance cannot exceed the maximum limit of {max_unverified} hours as per SEMO policy.")
        return True
    
    def validate_is_new_hire(self):
        if self.is_new_hire and self.verified_sick_balance <= 0:
            self.verified_sick_balance = self.sick_policy.upfront_verified
            self.unverified_sick_balance = self.sick_policy.max_unverified_sick_leave
            self.is_new_hire = False
            self.save()
        return True




    # This method is used to update the balance of verified sick leave balance and unverified sick leave balance based on the Sick Policy intender for the cron job to run biweekly.
    def accrue_biweekly(self):
        if self.fte < self.sick_policy.fte_threshold:
            raise ValueError("FTE must be greater than or equal to the Sick Policy's FTE threshold.")
        max_verified = self.sick_policy.max_unverified_sick_leave
        accrual = self.sick_policy.accrued_rate
        # Update the unverified sick leave balance can check cetain conditions
        if self.unverified_sick_balance < max_verified:
            room = max_verified - self.unverified_sick_balance
            to_add = min(room, accrual)
            self.unverified_sick_balance += to_add
            accrual -= to_add
        else: 
            raise ValueError("Unverified sick leave balance has reached its maximum limit.")
        # If there is still accrual left, add it to the verified sick leave balance
        if accrual > 0:
            self.verified_sick_balance += accrual
        else:
            raise ValueError("No accrual left to add to the verified sick leave balance.")
        
        
    def __str__(self):
        return f"{self.user.username} - Unverified Sick Leave Balance : {self.unverified_sick_balance} | Verified Sick Leave Balance : {self.verified_sick_balance}"

    class Meta:
        verbose_name = "Sick Leave Balance"
        verbose_name_plural = "Sick Leave Balances"
