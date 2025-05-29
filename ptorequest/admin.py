from django.contrib import admin
from django.utils.timezone import localtime
from .models import PTORequests 

@admin.register(PTORequests)
class PTORequestsAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'pay_types', 'formatted_start_date_time', 'formatted_end_date_time', 'total_hours', 'reason', 'status',)
    list_filter = ('status', 'department_name')
    list_editable = ('status',)
    search_fields = ('user__username', 'reason')
    def get_queryset(self, request):
        """
        Override the default queryset to ensure that only PTO requests
        belonging to the current user are displayed in the admin interface.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def formatted_start_date_time(self, obj):
        """Return start date time in 24-hour format (HH:MM:SS)."""
        if obj.start_date_time:
            # Convert to local time and format in 24-hour format (HH:MM:SS)
            return localtime(obj.start_date_time).strftime('%a %m/%d/%y  %H:%M')

        return None

    def formatted_end_date_time(self, obj):
        """Return end date time in 24-hour format (HH:MM:SS)."""
        if obj.end_date_time:
            # Convert to local time and format in 24-hour format (HH:MM:SS)
            return localtime(obj.end_date_time).strftime('%a %m/%d/%y  %H:%M')

        return None
    
    formatted_start_date_time.short_description = 'Start Date Time'
    formatted_start_date_time.admin_order_field = 'start_date_time'
    formatted_end_date_time.admin_order_field = 'end_date_time'
    formatted_end_date_time.short_description = 'End Date Time'




# Register your models here.
