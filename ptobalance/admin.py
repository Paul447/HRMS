from django.contrib import admin
from .models import PTOBalance
from .forms import PTOBalanceForm
from yearofexperience.models import YearOfExperience    
from accuralrates.models import AccrualRates

@admin.register(PTOBalance)
class PTOBalanceAdmin(admin.ModelAdmin):
    form  = PTOBalanceForm
    list_display = ('user', 'employee_type', 'pay_frequency', 'pto_balance', 'accrual_rate', 'year_of_experience')

    search_fields = ('user__username', 'employee_type__name', 'pay_frequency__frequency')    
    def save_model(self, request, obj, form, change):
        employeetype = obj.employee_type
        payfrequency = obj.pay_frequency
        yearofexperience = YearOfExperience.objects.filter(user=obj.user).first().years_of_experience 
        if yearofexperience < 1:
            x = 1
        elif yearofexperience < 2:
            x = 2
        elif yearofexperience < 3:
            x = 3
        elif yearofexperience < 4:
            x = 4
        elif yearofexperience < 5:
            x = 5
        elif yearofexperience < 6:
            x = 6
        elif yearofexperience < 7:
            x = 7
        elif yearofexperience < 8:
            x = 8
        elif yearofexperience < 9:
            x = 9
        elif yearofexperience < 10:
            x = 10
        else:
            x = 11
        accrualrate = AccrualRates.objects.filter(employee_type=employeetype, pay_frequency=payfrequency, year_of_experience=x).first()
        obj.accrual_rate = accrualrate
        ss = YearOfExperience.objects.filter(user=obj.user).first()
        obj.year_of_experience = ss

        return super().save_model(request, obj, form, change)
    
# Register your models here.
