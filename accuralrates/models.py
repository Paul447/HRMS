from django.db import models
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from django.core.validators import MinValueValidator


# Create your models here.
class AccrualRates(models.Model):
    EXPERIENCE_CHOICES = [(i, f"{i} Year(s)") for i in range(1, 12)]  # 1 to 11 years
    year_of_experience = models.IntegerField(choices=EXPERIENCE_CHOICES)
    accrual_rate = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0)])
    annual_accrual_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name="accrual_rates")
    pay_frequency = models.ForeignKey(Pay_Frequency, on_delete=models.CASCADE, related_name="accrual_rates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Accrual Rate"
        verbose_name_plural = "Accrual Rates"
        unique_together = ("year_of_experience", "employee_type", "pay_frequency")  # Prevent duplicate entries

    def __str__(self):
        return f"{self.year_of_experience} Years - {self.employee_type} - {self.pay_frequency}: {self.accrual_rate}"
