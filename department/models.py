from django.db import models


# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = "department_units"
        verbose_name = "Department Unit"
        verbose_name_plural = "Department Units"


class UserProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    is_time_off = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    class Meta:
        db_table = "employee_profiles"
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
