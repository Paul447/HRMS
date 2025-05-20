from django.contrib import admin

from .models import EmployeeType

@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 10

