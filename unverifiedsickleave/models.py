from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from sickpolicy.models import SickLeaveProratedValue, MaxSickValue

# Create your models here.


# On the basis of the accural rate, the sick leave balance will be updated using the cron job defined in this application,
# The Unverified Sick Leave Balance will be updated first to the maximum limit only then the Verified Sick Leave Balance will be updated.
# When updating the Verified Sick Leaves with the Accural Rate, the unverified sick leave must be checked first to ensure that it is at it's maximum limit.
# Create the automatic biweekly corn job to update the Sick Leave Balance based on the accrual rate.


class SickLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="sick_leave_balance")
    sick_prorated = models.ForeignKey(SickLeaveProratedValue, on_delete=models.CASCADE, related_name="sick_leave_balances")
    unverified_sick_balance = models.DecimalField(max_digits=13, decimal_places=10, default=0.0)
    verified_sick_balance = models.DecimalField(max_digits=14, decimal_places=10, default=0.0)
    used_FVSL = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text="Verified family care leave balance, maximum 96 hours per employee per year, not prorated by FTE.")
    is_new_hire = models.BooleanField(default=False, help_text="Indicates if the user is a new hire. If True, the verified sick leave balance will be initialized with the upfront verified sick leave from the SickLeaveProratedValue.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):  # Use Django's clean method for validation
        max_unverified = self.sick_prorated.prorated_unverified_sick_leave
        if self.unverified_sick_balance > max_unverified:
            raise ValidationError(f"Unverified sick leave balance cannot exceed the maximum limit of {max_unverified} hours as per SEMO policy.")

        # Validation for family care balance
        max_family_care_obj = MaxSickValue.objects.first()
        if not max_family_care_obj:
            raise ValidationError("Global MaxSickValue settings are missing. Please configure them.")
        if self.used_FVSL > max_family_care_obj.threshold_FVSL:
            raise ValidationError(f"Verified family care balance cannot exceed {max_family_care_obj.threshold_FVSL} hours per year.")

    def save(self, *args, **kwargs):
        # 1. First, run the full validation defined in clean()
        self.clean()

        # 2. Handle new hire initialization logic BEFORE saving
        if self.is_new_hire and self.verified_sick_balance <= 0:
            self.verified_sick_balance = self.sick_prorated.prorated_upfront_verified
            self.is_new_hire = False  # Set to False after initialization
        # self.accrue_biweekly()
        # 3. Now, call the original save method to store the data
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Sick Leave Balance"



    class Meta:
        verbose_name = "Sick Leave Balance"
        verbose_name_plural = "Sick Leave Balances"
