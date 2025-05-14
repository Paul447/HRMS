from django.db import models

# Create your models here.
class BiweeklyCron(models.Model):
    run_date = models.DateField(unique=True)
    is_active = models.BooleanField(default=True)
    tag = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Biweekly Cron"
        verbose_name_plural = "Biweekly Crons"