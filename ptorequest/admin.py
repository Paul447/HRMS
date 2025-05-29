from django.contrib import admin
from django.utils.timezone import localtime
from .models import PTORequests
from department.models import UserProfile

@admin.register(PTORequests)
class PTORequestsAdmin(admin.ModelAdmin):
    """
    Admin configuration for PTORequests model.
    Manages the display, filtering, and editing of PTO requests in the Django admin.
    """

    # --- Display Options ---
    list_display = (
        'user',
        'department_name',
        'pay_types',
        'formatted_start_date_time',
        'formatted_end_date_time',
        'total_hours',
        'reason',
        'status',
    )
    # Default filters and search fields (will be overridden for non-superusers)
    list_filter = (
        'status',
        'department_name',
        'start_date_time',
        'end_date_time',
    )
    search_fields = (
        'user__username',
        'reason',
    )
    list_per_page = 15

    # --- Editable Fields ---
    list_editable = (
        'status',
    )

    # --- Custom Methods for Display ---
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

    # --- Dynamic Filters and Search Fields ---
    def get_list_filter(self, request):
        """
        Dynamically adjusts the list filters based on the user's permissions.
        Superusers see all filters, regular users do not see 'department_name'.
        """
        if request.user.is_superuser:
            return self.list_filter
        return ('status', 'start_date_time', 'end_date_time',) # Exclude 'department_name'

    def get_search_fields(self, request):
        """
        Dynamically adjusts the search fields based on the user's permissions.
        Superusers can search by 'user__username' and 'reason', regular users only by 'reason'.
        """
        if request.user.is_superuser:
            return self.search_fields
        return ('reason',) # Exclude 'user__username'

    # --- Queryset Customization ---
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