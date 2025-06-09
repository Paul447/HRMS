from django.contrib import admin
from .models import LeaveType, DepartmentBasedLeaveType

class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)



class DepartmentBasedLeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('department', 'leave_type')
    search_fields = ('department__name', 'leave_type__name')
    ordering = ('department',)


# Register your models here.
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(DepartmentBasedLeaveType, DepartmentBasedLeaveTypeAdmin)