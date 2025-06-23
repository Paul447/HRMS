from django.contrib import admin
from django.utils.timezone import localtime
from .models import TimeoffRequest

# Register your models here.
@admin.register(TimeoffRequest)
class TimeoffreqAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'requested_leave_type',
        'formatted_start_date_time',
        'formatted_end_date_time',
        'time_off_duration',
        'employee_leave_reason',
        'status',
        'reference_pay_period',
        'document_proof',
        'reviewer',
        'reviewed_at',
    )
    list_filter = (
        'status',
        'employee',
        'requested_leave_type',
    )
    search_fields = (
        'employee__username',
        'employee_leave_reason',
    )
    list_editable = (
        'status', 
    )
    
    list_per_page = 15

    def formatted_start_date_time(self, obj):
        """
        Returns the start date and time of the PTO request, formatted for display.
        The format is 'Day Mon/DD/YY HH:MM' (e.g., 'Wed 05/29/25 10:30').
        """
        if obj.start_date_time:
            return localtime(obj.start_date_time).strftime('%a %m/%d/%y %H:%M')
        return None
    def formatted_end_date_time(self, obj):
        """
        Returns the end date and time of the PTO request, formatted for display.
        The format is 'Day Mon/DD/YY HH:MM' (e.g., 'Thu 05/30/25 17:00').
        """
        if obj.end_date_time:
            return localtime(obj.end_date_time).strftime('%a %m/%d/%y %H:%M')
        return None
    formatted_start_date_time.short_description = 'Start Date Time'
    formatted_start_date_time.admin_order_field = 'start_date_time'
    formatted_end_date_time.short_description = 'End Date Time'
    formatted_end_date_time.admin_order_field = 'end_date_time'
    def get_queryset(self, request):
        """
        Returns the queryset of PTO requests, filtered by user if not a superuser.
        Superusers can see all requests, while regular users only see their own requests.
        This method ensures that users can only access their own PTO requests unless they are superusers.
      
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
