# notifications_app/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'verb', 'content_object', 'read', 'level')
    list_filter = ('read', 'level',  'recipient__username', 'actor__username')
    search_fields = ('recipient__username', 'actor__username', 'verb', 'description')
    raw_id_fields = ('actor', 'recipient', 'content_type') # Use raw IDs for large user/contenttype lists
    # date_hierarchy = 'timestamp' # Adds a date drill-down navigation