from django.db import models
from django.contrib.auth.models import User


class Pay_Frequency(models.Model):
    frequency = models.CharField(max_length=100, unique=True)  # e.g., "Monthly", "Bi-Weekly"

    class Meta:
        verbose_name = "Pay Frequency"
        verbose_name_plural = "Pay Frequencies"

    def __str__(self):
        return self.frequency

