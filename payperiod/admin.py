from django.contrib import admin, messages
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone  # Still use Django's timezone for .localtime() for display

from .models import PayPeriod


@admin.register(PayPeriod)
class PayPeriodAdmin(admin.ModelAdmin):
    """
    Admin configuration for the PayPeriod model.
    Provides display, filtering, and custom actions for managing pay periods.
    """

    list_display = ["start_date", "end_date", "display_duration"]
    change_list_template = "admin/payperiod_changelist.html"  # Custom template for list view
    actions = ["filter_pay_periods_up_to_today_action"]  # Custom admin action

    # --- Custom Display Methods ---
    def display_duration(self, obj):
        """Calculates and displays the duration of the pay period."""
        duration = obj.end_date - obj.start_date
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{days}d, {hours}h, {minutes}m"

    display_duration.short_description = "Duration"

    # --- Custom Admin Actions ---
    def filter_pay_periods_up_to_today_action(self, request, queryset):
        """
        Admin action to filter and display pay periods up to today's date.
        """
        pay_periods = PayPeriod.get_pay_periods_up_to_today()

        if not pay_periods.exists():
            self.message_user(request, "No pay periods found up to today.", level=messages.INFO)
            return HttpResponseRedirect(request.get_full_path())

        response_content = "Pay periods up to today:\n\n"
        for period in pay_periods:
            # Use timezone.localtime() for display, which respects TIME_ZONE from settings
            local_start = timezone.localtime(period.start_date).strftime("%Y-%m-%d %H:%M %Z")
            local_end = timezone.localtime(period.end_date).strftime("%Y-%m-%d %H:%M %Z")
            response_content += f"  Start: {local_start}, End: {local_end}\n"

        return HttpResponse(response_content, content_type="text/plain")

    filter_pay_periods_up_to_today_action.short_description = "View Pay Periods Up to Today"

    # --- Custom Admin Views/URLs ---
    def get_urls(self):
        """
        Registers custom URLs for the PayPeriod admin.
        """
        urls = super().get_urls()
        custom_urls = [path("generate-pay-periods/", self.admin_site.admin_view(self.generate_pay_periods_view), name="payperiod_generate_pay_periods")]
        return custom_urls + urls

    def generate_pay_periods_view(self, request):
        """
        Admin view to trigger the generation of biweekly pay periods.
        """
        if request.method == "POST":
            num_periods_to_generate = 35  # Could be configurable via a form if desired

            created_count, initial_start_date = PayPeriod.generate_biweekly_pay_periods(num_periods=num_periods_to_generate)

            if created_count > 0:
                # Convert initial_start_date (which is timezone-aware) to local time for message
                local_initial_start = timezone.localtime(initial_start_date).strftime("%Y-%m-%d")
                self.message_user(request, f"Successfully created {created_count} biweekly pay periods starting from {local_initial_start}.", level=messages.SUCCESS)
            else:
                self.message_user(request, "No new pay periods were generated. They might already exist or an issue occurred.", level=messages.WARNING)
        else:
            self.message_user(request, "Please use POST request to generate pay periods.", level=messages.ERROR)

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "../"))
