from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class IsUnauthenticated(BasePermission):
    """
    Restrict access to only unauthenticated users, by manually checking the token.
    """

    def has_permission(self, request, view):
        # Attempt to authenticate using SimpleJWT
        jwt_authenticator = JWTAuthentication()

        try:
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is not None:
                # Valid token was found, user is authenticated
                return False
        except (InvalidToken, TokenError):
            # Invalid token, treat as unauthenticated
            pass

        return True  # No valid token found → user is unauthenticated
