# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrSuperuser(BasePermission):
    """
    Allow access only to the user themselves or superusers.
    """

    def has_permission(self, request, view):
        user_id = request.query_params.get("user_id")

        # Allow superusers full access
        if request.user.is_superuser:
            return True

        # If user_id is not provided, allow user to access their own data
        if not user_id:
            return True

        # If user_id is provided, ensure it matches the authenticated user
        return int(user_id) == request.user.id
