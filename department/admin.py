from django.contrib import admin
from .models import Department

admin.site.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    date_hierarchy = 'created_at'

# Register your models here.
