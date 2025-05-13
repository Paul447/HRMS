from django.db import models
from django.contrib.auth.models import User
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from yearofexperience.models import YearOfExperience
from accuralrates.models import AccrualRates


# Create your models here.
class PTOBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pto_balance")
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name="pto_balances")
    pay_frequency = models.ForeignKey(Pay_Frequency, on_delete=models.CASCADE, related_name="pto_balances")
    year_of_experience = models.OneToOneField(YearOfExperience, on_delete=models.CASCADE, related_name="pto_balances",editable=False)
    accrual_rate = models.ForeignKey(AccrualRates, on_delete=models.CASCADE, related_name="pto_balances",editable=False)
    pto_balance = models.FloatField(default=0.0)  # PTO balance field

    def calculate_initial_balance(self):
        """Calculate initial PTO balance based on accrual rate and experience."""
        return self.accrual_rate.accrual_rate  # Adjust logic based on your needs

    def __str__(self):
        return f"{self.user.username} - PTO: {self.pto_balance}"

    class Meta:
        verbose_name = "PTO Balance"
        verbose_name_plural = "PTO Balance"
