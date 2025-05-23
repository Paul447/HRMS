"""
Django Admin configuration for custom models and User model extensions.

This module registers custom models (Department, UserProfile) with the Django
admin site and customizes the default User model's admin interface to
include UserProfile fields inline.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Department, UserProfile # Ensure all models are imported here

# --- Department Model Admin ---

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    Provides a clear overview and efficient management of department records.
    """
    list_display = (
        'name',
    )
    search_fields = (
        'name',
    )
    ordering = (
        'name',
    )


# --- UserProfile Model Admin ---

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    Manages additional user-specific information, linked to Django's built-in User model.
    """
    list_display = (
        'user',
        'department'
    )
    search_fields = (
        'user__username', # Allows searching by username of the linked User
        'department__name' # Allows searching by department name
    )
    list_filter = (
        'department', # Provides a filter sidebar for departments
    )
    ordering = (
        'user__username', # Order UserProfiles by the linked user's username
    )

# --- Custom User Admin with UserProfile Inline ---

class UserProfileInline(admin.StackedInline):
    """
    Inline admin configuration for UserProfile.
    Allows UserProfile fields to be edited directly within the User admin page.
    """
    model = UserProfile
    can_delete = False # Prevent deletion of UserProfile when deleting a User
    verbose_name_plural = 'Profile' # Display name for the inline section in admin

class CustomUserAdmin(BaseUserAdmin):
    """
    Custom Admin configuration for Django's built-in User model.
    Extends the default User admin to include UserProfile fields inline.
    """
    inlines = (
        UserProfileInline,
    )
    # Inherit existing list_display, search_fields, etc., from BaseUserAdmin
    # You can customize them further if needed.
    # Example: add 'department_display' to list_display
    # list_display = BaseUserAdmin.list_display + ('department_display',)
    # def department_display(self, obj):
    #     # Ensure userprofile exists before accessing department
    #     if hasattr(obj, 'userprofile') and obj.userprofile.department:
    #         return obj.userprofile.department.name
    #     return '-'
    # department_display.short_description = 'Department'


# Unregister the default User admin before registering your custom one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass # User might not be registered yet if this admin.py is loaded early

# Register User with the new CustomUserAdmin
admin.site.register(User, CustomUserAdmin)