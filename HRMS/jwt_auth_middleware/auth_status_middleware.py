from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
import logging

from . import token_utils

logger = logging.getLogger(__name__)

class AuthStatusMiddleware(MiddlewareMixin):
    """
    Checks for an access token in cookies, verifies it, and sets the HTTP_AUTHORIZATION header if valid.
    Redirects authenticated users from the login page to the dashboard.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        login_url = reverse("hrmsauth:frontend_login")
        dashboard_url = reverse("hrmsauth:dashboard")

        # Validate redirect URLs
        host = request.get_host()
        if not (url_has_allowed_host_and_scheme(login_url, allowed_hosts={host}) and url_has_allowed_host_and_scheme(dashboard_url, allowed_hosts={host})):
            logger.error("Invalid redirect URL detected.")
            return None  # Skip processing to avoid open redirects

        # Redirect authenticated users from login page
        if access_token and request.path == login_url:
            if token_utils.verify_access_token(access_token):
                logger.debug("Authenticated user on login page. Redirecting to dashboard.")
                return redirect(dashboard_url)
            else:
                logger.warning("Expired or invalid access token on login page.")
                request.META.pop("HTTP_AUTHORIZATION", None)

        # Inject valid access token into Authorization header
        if access_token:
            if token_utils.verify_access_token(access_token):
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                logger.debug("Valid access token injected into Authorization header.")
            else:
                logger.warning("Invalid or expired access token. Clearing Authorization header.")
                request.META.pop("HTTP_AUTHORIZATION", None)
        else:
            logger.debug("No access token found. Clearing Authorization header.")
            request.META.pop("HTTP_AUTHORIZATION", None)

        return None