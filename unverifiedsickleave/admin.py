from django.contrib import admin


# Register your models here.
class SickLeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ["user", "sick_prorated", "unverified_sick_balance", "verified_sick_balance", "used_FVSL", "is_new_hire"]
    search_fields = ["user__username"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []
