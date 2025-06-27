from rest_framework import permissions
from department.models import UserProfile
from rest_framework import viewsets


class IsManagerOfDepartment(permissions.BasePermission):
    """
    Custom permission to allow only managers of the specific department to access requests.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Superusers bypass this permission check at the method level (get_permissions)
        # but this is here for general robustness if called directly
        if request.user.is_superuser:
            return True
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.is_manager
        except UserProfile.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Superusers bypass this object-level permission check as well
        if request.user.is_superuser:
            return True
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.is_manager and user_profile.department == obj.employee.userprofile.department
        except UserProfile.DoesNotExist:
            return False
