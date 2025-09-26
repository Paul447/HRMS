from django.db import models
from datetime import date


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
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    tenure = models.DecimalField(max_digits=4, decimal_places=2, default=0.0,null=True, editable=False)
    is_time_off = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    class Meta:
        db_table = "employee_profiles"
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"

    def calculate_tenure(self):
        """Return years of tenure based on user's date_joined."""
        if not getattr(self.user, "date_joined", None):
            return 0.0

        today = date.today()
        months = (today.year - self.user.date_joined.year) * 12 + (today.month - self.user.date_joined.month)

        return round(max(months, 0) / 12, 2)

    def save(self, *args, **kwargs):
        new_tenure = self.calculate_tenure()
        if self.tenure != new_tenure:
            self.tenure = new_tenure
        super().save(*args, **kwargs)
    