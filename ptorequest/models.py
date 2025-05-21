from django.db import models
from department.models import Department
from paytype.models import PayType

# Create your models here.
class PTORequests(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    department_name = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='pto_requests', null=False)
    pay_types = models.ForeignKey(PayType, on_delete=models.CASCADE, related_name='pto_requests', null=False)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, null=True,blank=True ) # Total hours requested
    reason = models.TextField() # Reason for PTO request
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    notes = models.TextField(blank=True, null=True) # Used by the approver to add comments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_hours(self):
        # Calculate the total hours between start_date_time and end_date_time
        if self.start_date_time and self.end_date_time:
            delta = self.end_date_time - self.start_date_time
            self.total_hours = delta.total_seconds() / 3600.0
            self.save()
        else:
            self.total_hours = 0.0
        return self.total_hours
    def __str__(self):
        return f"{self.user.username} - {self.department_name.name} - {self.start_date_time} to {self.end_date_time}"

