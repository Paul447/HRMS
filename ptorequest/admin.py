from django.contrib import admin
from .models import PTORequests 

admin.site.register(PTORequests)
class PTORequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'pay_types', 'start_date_time', 'end_date_time', 'total_hours', 'reason', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'department_name')
    search_fields = ('user__username', 'reason')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# Register your models here.
