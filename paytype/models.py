from django.db import models
from department.models import Department

class PayType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DepartmentBasedPayType(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    pay_type = models.ForeignKey(PayType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.department.name} - {self.pay_type.name}"
    
    class Meta:
        verbose_name = "Department Leave Type"
        verbose_name_plural = "Department  Leave Types"
        unique_together = ('department', 'pay_type')