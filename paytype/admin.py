from django.contrib import admin
from .models import PayType

admin.site.register(PayType)
class PayTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    

# Register your models here.
