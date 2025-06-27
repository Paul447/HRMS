from django.contrib import admin
from .models import Holiday


# Register your models here.
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "description", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("date",)


admin.site.register(Holiday, HolidayAdmin)
