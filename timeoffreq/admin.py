from django.contrib import admin
from django.utils.timezone import localtime
from django import forms
from django.contrib.admin import ModelAdmin
from .models import TimeoffRequest


class TimeoffRequestAdminForm(forms.ModelForm):
    """
    Custom form to add validation for status changes in non-pending requests.
    """

    class Meta:
        model = TimeoffRequest
        fields = "__all__"

        # In TimeoffRequestAdminForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("TimeoffRequestAdminForm __init__ called")

    def clean_status(self):
        print("clean_status called")
        status = self.cleaned_data.get("status")
        instance = self.instance
        print(f"  Current instance status: {instance.status if instance else 'N/A'}")
        print(f"  New status: {status}")

        if instance and instance.pk:
            if instance.status in ["approved", "rejected"] and status != instance.status:
                print(f"  Validation error raised: Cannot change from {instance.status}")
                raise forms.ValidationError("Cannot change the status of a request that is already '%s'." % instance.status)
        return status


@admin.register(TimeoffRequest)
class TimeoffreqAdmin(ModelAdmin):
    form = TimeoffRequestAdminForm
    list_display = ("employee", "requested_leave_type", "formatted_start_date_time", "formatted_end_date_time", "time_off_duration", "employee_leave_reason", "status", "reference_pay_period", "document_proof", "reviewer", "reviewed_at")
    list_filter = ("status", "employee", "requested_leave_type")
    search_fields = ("employee__username", "employee_leave_reason")
    # Remove 'status' from list_editable if you want to completely prevent in-list editing for approved/rejected.
    # If 'status' remains in list_editable, the form's clean_status will still prevent the save.
    list_editable = ("status",)
    list_per_page = 15
    exclude = ("time_off_duration", "status", "reference_pay_period", "reviewer", "reviewed_at")  # Keep status here if you want it editable only via the form, not list_editable

    def formatted_start_date_time(self, obj):
        """
        Returns the start date and time of the PTO request, formatted for display.
        The format is 'Day Mon/DD/YY HH:MM' (e.g., 'Wed 05/29/25 10:30').
        """
        if obj.start_date_time:
            return localtime(obj.start_date_time).strftime("%a %m/%d/%y %H:%M")
        return None

    def formatted_end_date_time(self, obj):
        """
        Returns the end date and time of the PTO request, formatted for display.
        The format is 'Day Mon/DD/YY HH:MM' (e.g., 'Thu 05/30/25 17:00').
        """
        if obj.end_date_time:
            return localtime(obj.end_date_time).strftime("%a %m/%d/%y %H:%M")
        return None

    formatted_start_date_time.short_description = "Start Date Time"
    formatted_start_date_time.admin_order_field = "start_date_time"
    formatted_end_date_time.short_description = "End Date Time"
    formatted_end_date_time.admin_order_field = "end_date_time"

    def get_queryset(self, request):
        """
        Returns the queryset of PTO requests, filtered by employee if not a superuser.
        Superusers can see all requests, while regular users only see their own requests.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee=request.user)

    def save_model(self, request, obj, form, change):
        """
        Custom save logic to handle status changes and set reviewer/reviewed_at.
        """
        # Check if the status is actually changing and the new status is 'approved' or 'rejected'
        if change and form.initial.get("status") != obj.status and obj.status in ["approved", "rejected"]:
            obj.reviewer = request.user
            obj.reviewed_at = localtime()
        super().save_model(request, obj, form, change)
