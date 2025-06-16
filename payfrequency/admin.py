from django.contrib import admin
from .models import Pay_Frequency

@admin.register(Pay_Frequency)
class PayFrequencyAdmin(admin.ModelAdmin):
    list_display = ('frequency',  'created_at', 'updated_at')
    search_fields = ('frequency',)
    list_filter = ('frequency',)
    ordering = ('frequency',)
    list_per_page = 10



# Register your models here.
