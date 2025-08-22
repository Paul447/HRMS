from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()  # Best practice for referencing the User model


class YearOfExperience(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="experience")
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, editable=False)  # Auto-calculated field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "experience_years"   # or keep "user_experience_years" if user-specific
        verbose_name = "Years of Experience"
        verbose_name_plural = "Years of Experience"

    def calculate_experience(self):
        """
        Calculate experience in years based on the user's `date_joined` (or a more
        appropriate hire_date field if available).
        """
        # It's better to use `date_joined` from the user model as the starting point.
        # Ensure your User model has a `date_joined` field or use a custom `hire_date`.
        if not self.user or not self.user.date_joined:
            # Handle cases where user or date_joined might be missing, though OneToOneField
            # makes `self.user` guaranteed if an instance exists.
            # A user might not have a date_joined if not properly set.
            return 0.0

        today = date.today()
        # Calculate total months difference.
        # This formula is generally robust for month-based experience calculation.
        months = (today.year - self.user.date_joined.year) * 12 + (today.month - self.user.date_joined.month)

        # Ensure experience doesn't go below zero if date_joined is in the future (unlikely but good to guard).
        if months < 0:
            return 0.0

        # Convert months to years and round to two decimal places for precision.
        return round(months / 12, 2)

    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate and update `years_of_experience`
        before the object is saved to the database.
        """
        # This ensures that `years_of_experience` is always up-to-date whenever
        # a YearOfExperience instance is created or explicitly saved.
        # However, for periodic updates for *all* users, the cron job is still needed
        # as `save()` isn't called automatically on existing instances over time.
        self.years_of_experience = self.calculate_experience()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Experience: {self.years_of_experience} years"
