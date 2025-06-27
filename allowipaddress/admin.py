from django.contrib import admin
from .models import AllowIpAddress

# Register your models here.


class AllowIpAddressAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "description", "is_active", "created_at", "updated_at")
    search_fields = ("ip_address", "description")
    list_filter = ("is_active",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
