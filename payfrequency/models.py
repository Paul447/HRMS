from django.db import models
from django.contrib.auth.models import User


class pay_frequency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pay_frequency')
    frequency = models.CharField(max_length=100, unique=True)  # e.g., "Monthly", "Bi-Weekly"

    class Meta:
        verbose_name = "Pay Frequency"
        verbose_name_plural = "Pay Frequencies"

    def __str__(self):
        return self.frequency

