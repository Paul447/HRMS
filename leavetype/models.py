from django.db import models
from department.models import Department

class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DepartmentBasedLeaveType(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.department.name} - {self.leave_type.name}"

    class Meta:
        verbose_name = "Department Leave Type"
        verbose_name_plural = "Department Leave Types"
        unique_together = ('department', 'leave_type')