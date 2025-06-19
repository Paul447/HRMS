from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# On the basis of the accural rate, the sick leave balance will be updated using the cron job defined in this application,
# The Unverified Sick Leave Balance will be updated first to the maximum limit only then the Verified Sick Leave Balance will be updated.
# When updating the Verified Sick Leaves with the Accural Rate, the unverified sick leave must be checked first to ensure that it is at it's maximum limit.
# Create the automatic biweekly corn job to update the Sick Leave Balance based on the accrual rate.
class SickLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sick_leave_balance")
    unverified_sick_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Sick leave balance field
    verified_sick_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Verified sick leave balance field
    sick_leave_accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Sick leave accrual rate field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Unverified Sick Leave Balance : {self.unverified_sick_leave_balance} | Verified Sick Leave Balance : {self.verified_sick_leave_balance}"

    class Meta:
        verbose_name = "Sick Leave Balance"
        verbose_name_plural = "Sick Leave Balances"
