from django.db import models
from department.models import Department
from paytype.models import PayType
from django.contrib.auth.models import User

class PTORequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department_name = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='pto_requests')
    pay_types = models.ForeignKey(PayType, on_delete=models.CASCADE, related_name='pto_requests')
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total_hours on save
        if self.start_date_time and self.end_date_time:
            delta = self.end_date_time - self.start_date_time
            self.total_hours = round(delta.total_seconds() / 3600.0, 2)
        else:
            self.total_hours = 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.department_name.name} - {self.start_date_time} to {self.end_date_time}"
