from django.db import models
from employeetype.models import EmployeeType
from payfrequency.models import pay_frequency


# Create your models here.
class AccrualRates(models.Model):
    EXPERIENCE_CHOICES = [(i, f"{i} Year(s)") for i in range(1, 12)]  # 1 to 11 years
    year_of_experience = models.IntegerField(choices=EXPERIENCE_CHOICES)  
    accrual_rate = models.FloatField(default=0.0)  # e.g., 1.5 hours per pay period
    annual_accrual_rate = models.FloatField(default=0.0)  # e.g., 18 hours per year
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name="accrual_rates")
    pay_frequency = models.ForeignKey(pay_frequency, on_delete=models.CASCADE, related_name="accrual_rates")

    class Meta:
        verbose_name = "Accrual Rate"
        verbose_name_plural = "Accrual Rates"
        unique_together = ('year_of_experience', 'employee_type', 'pay_frequency')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.year_of_experience} Years - {self.employee_type} - {self.pay_frequency}: {self.accrual_rate}"