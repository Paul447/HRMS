from django.contrib import admin
from .models import PayType,  DepartmentBasedPayType


class PayTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    date_hierarchy = 'created_at'



class DepartmentBasedPayTypeAdmin(admin.ModelAdmin):
    list_display = ('department', 'pay_type')
    search_fields = ('department__name', 'pay_type__name')
    ordering = ('department',)


# Register your models here.
admin.site.register(PayType, PayTypeAdmin)
admin.site.register(DepartmentBasedPayType, DepartmentBasedPayTypeAdmin)