from django.db import models
from django.contrib.auth.models import User
from datetime import date
# Create your models here.
class YearOfExperience(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="experience")
    years_of_experience = models.FloatField(editable=False)  # Auto-calculated field
    
    def calculate_experience(self):
        """Calculate experience in years based on date_joined."""
        today = date.today()
        months = (today.year - self.user.date_joined.year) * 12 + (today.month - self.user.date_joined.month)
        return round(months / 12, 2)  # Convert months to years

    def save(self, *args, **kwargs):
        """Override save to update years_of_experience before storing."""
        self.years_of_experience = self.calculate_experience()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.years_of_experience} years"

    class Meta:
        verbose_name = "Year of Experience"
        verbose_name_plural = "Years of Experience"