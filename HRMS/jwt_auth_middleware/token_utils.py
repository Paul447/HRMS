import logging
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger(__name__)

def verify_access_token(token):
    """Verifies an access token and returns True if valid, False otherwise."""
    if not token:
        logger.debug("No access token provided for verification.")
        return False
    try:
        access_token = AccessToken(token)
        access_token.verify()
        # Optionally validate token scope here if applicable
        return True
    except TokenError as e:
        if "expired" in str(e).lower():
            logger.info(f"Access token expired: {e}")
        else:
            logger.warning(f"Invalid access token: {e}")
        return False

def refresh_access_token(refresh_token_str):
    """
    Attempts to refresh an access token using a refresh token.
    Returns (new_access_token, new_refresh_token, None) on success,
    or (None, None, error_message) on failure.
    """
    if not refresh_token_str:
        logger.debug("No refresh token provided.")
        return None, None, "no_refresh_token"

    try:
        refresh = RefreshToken(refresh_token_str)
        new_access_token = str(refresh.access_token)
        new_refresh_token = None

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            User = get_user_model()
            user_id = refresh.get("user_id")
            try:
                user = User.objects.get(id=user_id)
                new_refresh_token = str(RefreshToken.for_user(user))
                if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
                    refresh.blacklist()
                    logger.debug("Old refresh token blacklisted after rotation.")
            except User.DoesNotExist:
                logger.warning("User not found during refresh rotation.")
                return None, None, "user_not_found"

        logger.info("Access token refreshed successfully.")
        return new_access_token, new_refresh_token, None
    except TokenError as e:
        logger.warning(f"Refresh token operation failed: {e}")
        return None, None, str(e)

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
        return False