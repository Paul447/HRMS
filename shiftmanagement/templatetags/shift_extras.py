# shiftmanagement/templatetags/shift_extras.py

from django import template

register = template.Library()

@register.filter
def get_display_name(user):
    """
    Returns the user's full name if available, otherwise their username.
    Handles cases where user might be None or not have a full name.
    """
    if user:
        full_name = user.get_full_name()
        if full_name:
            return full_name
        return user.username
    return "" # Return empty string if user is None