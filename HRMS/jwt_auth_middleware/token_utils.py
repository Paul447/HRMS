import logging
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_access_token(token):
    """Verifies an access token and returns True if valid, False otherwise."""
    if not token:
        return False
    try:
        AccessToken(token).verify()
        return True
    except TokenError as e:
        logger.debug(f"Access token verification failed: {e}")
        return False


def refresh_access_token(refresh_token_str):
    """
    Attempts to refresh an access token using a refresh token.
    Returns (new_access_token, new_refresh_token, None) on success,
    or (None, None, error_message) on failure.
    """
    if not refresh_token_str:
        return None, None, "No refresh token provided."

    try:
        refresh = RefreshToken(refresh_token_str)
        new_access_token = str(refresh.access_token)
        new_refresh_token = None

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            User = get_user_model()
            user_id = refresh["user_id"]
            try:
                user = User.objects.get(id=user_id)
                new_refresh_token = str(RefreshToken.for_user(user))
                if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
                    refresh.blacklist()
                    logger.debug("Old refresh token blacklisted after rotation.")
            except User.DoesNotExist:
                logger.warning(f"User with ID {user_id} not found during refresh rotation. Invalidating session.")
                return None, None, "user_not_found"  # Specific error for user not found

        logger.info("Access token refreshed successfully.")
        return new_access_token, new_refresh_token, None
    except TokenError as e:
        logger.warning(f"Refresh token operation failed: {e}")
        return None, None, str(e)
    except Exception as e:
        logger.error(f"An unexpected error occurred during token refresh: {e}")
        return None, None, "unexpected_error"


def blacklist_refresh_token(refresh_token_str):
    """Blacklists a given refresh token."""
    if not refresh_token_str:
        logger.debug("No refresh token to blacklist.")
        return False
    try:
        RefreshToken(refresh_token_str).blacklist()
        logger.info("Refresh token blacklisted successfully.")
        return True
    except TokenError as e:
        logger.warning(f"Failed to blacklist refresh token: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during refresh token blacklisting: {e}")
    return False
