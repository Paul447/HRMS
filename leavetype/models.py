from django.db import models
from department.models import Department


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = "leave_types"
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"


class DepartmentBasedLeaveType(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.department.name} - {self.leave_type.name}"

    class Meta:
        db_table = "unit_based_leave_types"
        verbose_name = "Unit Leave Type"
        verbose_name_plural = "Unit Leave Types"
        unique_together = ("department", "leave_type")
