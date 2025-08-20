# timeclock_security/models.py (or similar app name)
from django.db import models


class AllowIpAddress(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'Main Office IP'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Whitelisted IP Address"
        verbose_name_plural = "Whitelisted IP Address"
        db_table = "whitelisted_ip_addresses"

    def __str__(self):
        return self.ip_address
