from django.contrib import admin
from .models import PTOBalance

@admin.register(PTOBalance)
class PTOBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_type', 'pay_frequency', 'year_of_experience', 'accrual_rate', 'pto_balance')

    search_fields = ('user__username', 'employee_type__type', 'pay_frequency__frequency')
    list_filter = ('employee_type', 'pay_frequency', 'year_of_experience', 'accrual_rate')
    ordering = ('user',)
    list_per_page = 10
    
# Register your models here.
