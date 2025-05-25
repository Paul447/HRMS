from django.contrib import admin
from django.db import models
from .models import PTOBalance, AccrualRates, YearOfExperience

@admin.register(PTOBalance)
class PTOBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_type', 'pay_frequency', 'pto_balance', 'accrual_rate', 'display_year_of_experience')
    search_fields = ('user__username', 'employee_type__name', 'pay_frequency__frequency')

    def display_year_of_experience(self, obj):
        try:
            return obj.user.experience.years_of_experience
        except YearOfExperience.DoesNotExist:
            return "N/A"
    display_year_of_experience.short_description = 'Years of Experience'
    display_year_of_experience.admin_order_field = 'user__experience__years_of_experience'

    def save_model(self, request, obj, form, change):
        employeetype = obj.employee_type
        payfrequency = obj.pay_frequency

        try:
            user_experience_obj = obj.user.experience
            year_of_experience_value = user_experience_obj.years_of_experience
        except YearOfExperience.DoesNotExist:
            year_of_experience_value = 0.0
            user_experience_obj = None
            print(f"Warning: YearOfExperience record missing for user {obj.user.username}") # Consider using logger.warning here

        thresholds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        x = 1
        for threshold in thresholds:
            if year_of_experience_value < threshold:
                x = threshold
                break
        else:
            x = 11

        accrualrate = AccrualRates.objects.filter(
            employee_type=employeetype,
            pay_frequency=payfrequency,
            year_of_experience=x
        ).first()

        if accrualrate:
            obj.accrual_rate = accrualrate
        else:
            obj.accrual_rate = None
            print(f"Warning: No AccrualRate found for EType:{employeetype.name}, PFreq:{payfrequency.frequency}, YOE:{x}") # Consider using logger.error here

        obj.year_of_experience = user_experience_obj

        super().save_model(request, obj, form, change)