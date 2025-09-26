from django.contrib import admin
import math
from django.db import models
from .models import PTOBalance, AccrualRates, YearOfExperience


@admin.register(PTOBalance)
class PTOBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "employee_type", "pay_frequency", "pto_balance", "accrual_rate", "display_year_of_experience")
    search_fields = ("user__username", "employee_type__name", "pay_frequency__frequency")

    def display_year_of_experience(self, obj):
        try:
            return obj.user.experience.years_of_experience
        except YearOfExperience.DoesNotExist:
            return "N/A"

    display_year_of_experience.short_description = "Years of Experience"
    display_year_of_experience.admin_order_field = "user__experience__years_of_experience"

    def save_model(self, request, obj, form, change):
        employeetype = obj.employee_type
        payfrequency = obj.pay_frequency

        user_experience_obj = getattr(obj.user, 'experience', None)
        year_of_experience_value = getattr(user_experience_obj, 'years_of_experience', 0.0)

        if user_experience_obj is None:
            print(f"Warning: YearOfExperience record missing for user {obj.user.username}")

        # Simple threshold calculation
        x = min(max(math.ceil(year_of_experience_value), 1), 11)

        # Fetch accrual rate
        accrualrate = AccrualRates.objects.filter(
            employee_type=employeetype,
            pay_frequency=payfrequency,
            year_of_experience=x
        ).first()

        if accrualrate:
            obj.accrual_rate = accrualrate
        else:
            obj.accrual_rate = None
            print(f"Warning: No AccrualRate found for EType:{employeetype.name}, PFreq:{payfrequency.frequency}, YOE:{x}")

        obj.year_of_experience = user_experience_obj

        super().save_model(request, obj, form, change)
