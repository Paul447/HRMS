from django.contrib import admin
from .models import PayType, UserBasedPayType


class PayTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    date_hierarchy = 'created_at'



class UserBasedPayTypeAdmin(admin.ModelAdmin):
    list_display = ('user', 'pay_type')
    search_fields = ('user__username', 'pay_type__name')
    ordering = ('user',)

# Register your models here.
admin.site.register(PayType, PayTypeAdmin)
admin.site.register(UserBasedPayType, UserBasedPayTypeAdmin)