from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class SickLeaveProratedValue(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Policy name (e.g., 'Full-Time', 'Part-Time', '70% Policy').")
    # Full-Time Equivalent (FTE) value for the policy,  For Full-Time employees, this should be 1.0, for Part-Time employees, this should be 0.5, It always have to be more than 0.5 on the basis of SEMO Policy.
    fte_value = models.DecimalField(max_digits=3, decimal_places=2, help_text="FTE value: 1.0 for Full-Time, >0.5 for Part-Time (per SEMO policy).", validators=[MinValueValidator(0.5), MaxValueValidator(1.0)])
    # Automatically Calculated on the basis of base max Value which is used for 1.0 FTE. Maximum unverified sick leave is prorated by FTE (e.g., 64 hrs for Full-Time, 32 hrs for Part-Time) and must be calculated based on the FTE value. Use reference Validation before crediting balance in the SickLeaveBalance model per policy.
    prorated_unverified_sick_leave = models.DecimalField(max_digits=5, decimal_places=2, help_text="Base unverified sick leave 64 hrs. Automatically Prorated by FTE. Don't Modify unless the policy changes maximum value.", null=True, blank=True)
    # Upfront verified sick leave is prorated based on FTE (e.g., 96 hrs at FTE 1.0, 48 hrs at 0.5 FTE), calculated from the FTE value. It should be initialized as the starting balance for currently hired users, with no validation required due to unlimited accrual.
    prorated_upfront_verified = models.DecimalField(max_digits=5, decimal_places=2, help_text="Base upfront verified sick leave 96 hrs. Automatically Prorated by FTE. Don't Modify unless the policy changes upfront verified sick leave value.", null=True, blank=True)

    class Meta:
        db_table = "sick_leave_prorated_values"
        verbose_name = "Sick Leave Prorated Value"
        verbose_name_plural = "Sick Leave Prorated Values"
        unique_together = ("name", "fte_value")

    def __str__(self):
        return f"{self.name} - FTE: {self.fte_value}, Unverified Sick Leave: {self.prorated_unverified_sick_leave}, Upfront Verified: {self.prorated_upfront_verified}"

    def get_prorated_max_unverified_sick_leave(self):
        """
        Calculate the maximum unverified sick leave based on the FTE value.
        This method is used to validate the SickLeaveBalance model before crediting balance.
        """
        if self.fte_value < 0.5:
            raise ValueError("FTE must be greater than or equal to 0.5.")
        max_leave = MaxSickValue.objects.first()
        if not max_leave:
            raise ValueError("MaxSickValue instance not found. Please create one.")
        return max_leave.max_unverified_sick_leave * self.fte_value

    def get_upfront_verified_sick_leave_per_fte(self):
        """
        Calculate the upfront verified sick leave based on the FTE value.
        This method is used to initialize the SickLeaveBalance model for new hires.
        """
        if self.fte_value < 0.5:
            raise ValueError("FTE must be greater than or equal to 0.5.")
        max_prorated = MaxSickValue.objects.first()
        if not max_prorated:
            raise ValueError("MaxSickValue instance not found. Please create one.")
        # Calculate the upfront verified sick leave based on the FTE value
        return max_prorated.upfront_verified * self.fte_value

    def save(self, *args, **kwargs):
        self.prorated_unverified_sick_leave = self.get_prorated_max_unverified_sick_leave()
        self.prorated_upfront_verified = self.get_upfront_verified_sick_leave_per_fte()
        super().save(*args, **kwargs)


class MaxSickValue(models.Model):
    """
    This model is used to store the maximum sick leave value for the SickPolicy model.
    It is used to validate the SickLeaveBalance model before crediting balance.
    """

    max_unverified_sick_leave = models.DecimalField(max_digits=5, decimal_places=2, default=64.0, help_text="Base unverified sick leave 64 hrs. Automatically Prorated by FTE. Don't Modify unless the policy changes maximum value.")
    upfront_verified = models.DecimalField(max_digits=5, decimal_places=2, default=96.0, help_text="Base upfront verified sick leave 96 hrs. Automatically Prorated by FTE. Don't Modify unless the policy changes upfront verified sick leave value.")
    accrued_rate = models.DecimalField(max_digits=11, decimal_places=10, default=2.4615384615, help_text="Fixed monthly accrual rate. Not prorated by FTE.")
    threshold_FVSL = models.DecimalField(max_digits=5, decimal_places=2, default=96.0, help_text="Max 96 hrs/year for verified family care. Not prorated. Resets yearly.")

    class Meta:
        db_table = "sick_leave_constants"
        verbose_name = "Sick Leave Constants value (Global)"
        verbose_name_plural = "Sick Leave Constants (Global)"

    def save(self, *args, **kwargs):
        if MaxSickValue.objects.exists() and not self.pk:
            raise ValueError("Only one MaxSickValue instance allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Max Sick Value: {self.max_unverified_sick_leave}, Upfront Verified: {self.upfront_verified}, Accrued Rate: {self.accrued_rate}, Family Care Limit: {self.threshold_FVSL}"


# # Signal to update SickLeaveProratedValue when MaxSickValue is saved
# def update_sick_leave_prorated(sender, instance, **kwargs):
#     """
#     Update SickLeaveProratedValue instances when MaxSickValue is saved.
#     This ensures that the prorated values are always in sync with the global max sick value.
#     """
#     SickLeaveProratedValue.objects.all().update(
#         prorated_unverified_sick_leave=instance.max_unverified_sick_leave,
#         prorated_upfront_verified=instance.upfront_verified
#     )
# post_save.connect(update_sick_leave_prorated, sender=MaxSickValue)
@receiver(post_save, sender=MaxSickValue)
def update_sick_leave_prorated(sender, instance, **kwargs):
    """
    Update SickLeaveProratedValue instances when MaxSickValue is saved.
    This ensures that the prorated values are always in sync with the global max sick value.
    """
    for obj in SickLeaveProratedValue.objects.all():
        obj.save()
