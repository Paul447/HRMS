from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Clock



@admin.register(Clock)
class ClockAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the Clock model.
    Provides enhanced display, filtering, search, and custom actions
    for managing user clock-in/clock-out entries.
    """

    list_display = ("user", "formatted_clock_in_time", "formatted_clock_out_time", "hours_worked", "pay_period_display", "status_display", "is_holiday")
    list_filter = ("user", "pay_period", "is_holiday")  # Allow filtering by user and associated pay period
    search_fields = ("user__username", "user__first_name", "user__last_name")  # Search by user's name
    readonly_fields = ("hours_worked", "pay_period")  # These fields are automatically calculated/assigned

    # Organize fields in the add/change form
    fieldsets = ((None, {"fields": ("user", "clock_in_time", "clock_out_time", "is_holiday")}), ("Calculated Information (Auto-filled)", {"fields": ("hours_worked", "pay_period"), "classes": ("collapse",), "description": "These fields are automatically computed based on clock times."}))  # Clearer title  # Make this section collapsible by default

    # Add custom actions to the admin list view
    actions = ["clock_out_selected"]

    def get_queryset(self, request):
        """
        Optimizes queryset to prefetch related user and pay period objects,
        reducing database queries in the list view.
        """
        return super().get_queryset(request).select_related("user", "pay_period")

    def formatted_clock_in_time(self, obj):
        """
        Returns the clock-in time formatted for the local timezone
        (e.g., "Mon 05/26/25 09:00 AM").
        """
        if obj.clock_in_time:
            return timezone.localtime(obj.clock_in_time).strftime("%a %m/%d/%y %I:%M %p")
        return "N/A"

    formatted_clock_in_time.admin_order_field = "clock_in_time"
    formatted_clock_in_time.short_description = "Clock In"

    def formatted_clock_out_time(self, obj):
        """
        Returns the clock-out time formatted for the local timezone,
        or indicates if the user is still clocked in.
        """
        if obj.clock_out_time:
            return timezone.localtime(obj.clock_out_time).strftime("%a %m/%d/%y %I:%M %p")
        return "Still Clocked In"  # More descriptive for null clock_out_time

    formatted_clock_out_time.admin_order_field = "clock_out_time"
    formatted_clock_out_time.short_description = "Clock Out"

    def pay_period_display(self, obj):
        """
        Displays the formatted string representation of the associated Pay Period.
        """
        if obj.pay_period:
            return str(obj.pay_period)
        return "N/A"

    pay_period_display.admin_order_field = "pay_period__start_date"  # Allows sorting by pay period's start date
    pay_period_display.short_description = "Pay Period"

    def status_display(self, obj):
        """
        Indicates the current status of the clock entry (Clocked In/Out).
        """
        if obj.clock_in_time and not obj.clock_out_time:
            return "Clocked In"
        elif obj.clock_in_time and obj.clock_out_time:
            return "Clocked Out"
        return "Invalid Entry"  # Should ideally not be reached if clock_in_time is always present

    status_display.short_description = "Status"

    def get_form(self, request, obj=None, **kwargs):
        """
        Customizes the form for adding/changing Clock entries.
        Pre-fills `clock_in_time` with the current time for new entries.
        """
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new entries
            # Set initial clock_in_time to the current local time for convenience
            form.base_fields["clock_in_time"].initial = timezone.localtime(timezone.now())
        return form

    def add_view(self, request, form_url="", extra_context=None):
        """
        Overrides the add view to prevent a user from creating a new clock-in
        entry if they are already actively clocked in.
        """
        if request.method == "GET":
            if request.user.is_authenticated and not request.user.is_superuser:
                # Check for an existing open clock entry for the current user
                active_clock = Clock.objects.filter(user=request.user, clock_out_time__isnull=True).first()
                if active_clock:
                    messages.warning(request, f"You are already clocked in since {timezone.localtime(active_clock.clock_in_time).strftime('%a %m/%d/%y %I:%M %p')}. Please clock out first or edit your existing entry.")
                    # Redirect to the change list view to show existing entries
                    return HttpResponseRedirect("../")
        return super().add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Custom save logic for the admin form.
        Allows the model's `save()` method to handle all automatic assignments and calculations.
        """
        # The model's save method now robustly handles pay_period assignment and hours calculation,
        # including the splitting of weekend shifts.
        super().save_model(request, obj, form, change)

        if not change and not obj.clock_out_time:
            messages.success(request, "Clock-in successful. Remember to clock out!")
        elif obj.clock_in_time and obj.clock_out_time:
            messages.success(request, f"Clock entry updated. Hours worked: {obj.hours_worked:.2f}")

    def clock_out_selected(self, request, queryset):
        """
        Admin action to clock out selected entries that are currently open.
        Sets their `clock_out_time` to the current time and triggers hour calculation.
        """
        # Filter for entries that are currently clocked in (clock_out_time is null)
        open_clocks = queryset.filter(clock_out_time__isnull=True)
        count = 0
        for clock_entry in open_clocks:
            clock_entry.clock_out_time = timezone.now()  # Set clock-out time to now (UTC)
            # Call save with calculate_hours=True to ensure hours are calculated
            # and potential splitting occurs.
            clock_entry.save(calculate_hours=True)
            count += 1

        if count > 0:
            self.message_user(request, f"Successfully clocked out {count} selected entries.", level=messages.SUCCESS)
        else:
            self.message_user(request, "No open clock entries were selected for clock out.", level=messages.INFO)

    clock_out_selected.short_description = "Clock Out Selected Open Entries"
