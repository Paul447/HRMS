from django.contrib import admin


# Register your models here.
# from sickpolicy.models import SickLeaveProratedValue

class SickLeaveProratedValueAdmin(admin.ModelAdmin):
    readonly_fields = ['prorated_unverified_sick_leave', 'prorated_upfront_verified']
    list_display = ['name', 'fte_value', 'prorated_unverified_sick_leave', 'prorated_upfront_verified']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            # No fields readonly when editing (make all editable)
            return []
        # While adding, don't allow editing prorated fields
        return self.readonly_fields

    def get_fields(self, request, obj=None):
        # Show all fields both while adding and editing
        return [
            'name',
            'fte_value',
            'prorated_unverified_sick_leave',
            'prorated_upfront_verified',
        ]

class MaxSickValueAdmin(admin.ModelAdmin):
    list_display = ['max_unverified_sick_leave', 'upfront_verified', 'accrued_rate','allow_verified_family_care_limit']
    # list_editable = [
    #     'max_unverified_sick_leave',
    #     'upfront_verified',
    #     'accrued_rate',
    #     'allow_verified_family_care_limit',
    # ]
    # Everything view and edit 
    