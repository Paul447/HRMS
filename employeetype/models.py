from django.db import models

# Create your models here.
class EmployeeType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Full-Time", "Part-Time"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name