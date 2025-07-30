from django.contrib import admin

from .models import AccrualRates


@admin.register(AccrualRates)
class AccrualRatesAdmin(admin.ModelAdmin):
    list_display = ("year_of_experience", "accrual_rate", "annual_accrual_rate", "employee_type", "pay_frequency")
    search_fields = ("year_of_experience__years_of_experience", "employee_type__type")
    list_filter = ("employee_type", "pay_frequency")
    ordering = ("year_of_experience",)
    list_per_page = 10


# Register your models here.
