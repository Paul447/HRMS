from django.contrib import admin

from .models import BiweeklyCron

@admin.register(BiweeklyCron)
class BiweeklyCronAdmin(admin.ModelAdmin):
    list_display = ('run_date', 'is_active', 'tag')
    search_fields = ('run_date', 'tag')
    list_filter = ('is_active',)
    ordering = ('-run_date',)
    list_per_page = 10


# Register your models here.
