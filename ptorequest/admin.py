from django.contrib import admin
from .models import PTORequests 

@admin.register(PTORequests)
class PTORequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'pay_types', 'start_date_time', 'end_date_time', 'total_hours', 'reason', 'status',)
    list_filter = ('status', 'department_name')
    list_editable = ('status',)
    search_fields = ('user__username', 'reason')



# Register your models here.
