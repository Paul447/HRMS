from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import logging

from . import token_utils

logger = logging.getLogger(__name__)

class AuthStatusMiddleware(MiddlewareMixin):
    """
    Checks for an access token in cookies, verifies it, and
    sets the HTTP_AUTHORIZATION header if valid. Also handles
    redirects for authenticated users accessing the login page.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        
        login_url = reverse('frontend_login')
        dashboard_url = reverse('dashboard')

        # If user is already authenticated and tries to access the login page, redirect them.
        if access_token and request.path == login_url:
            if token_utils.verify_access_token(access_token):
                logger.debug("AuthStatusMiddleware: Authenticated user on login page. Redirecting to dashboard.")
                return redirect(dashboard_url)
            else:
                logger.debug("AuthStatusMiddleware: Expired/invalid access token on login page. Allowing access.")
                # Clear header if token is bad, so DRF doesn't try to use it
                request.META.pop("HTTP_AUTHORIZATION", None)

        # For any other request, if an access token exists and is valid, inject it.
        if access_token:
            if token_utils.verify_access_token(access_token):
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                logger.debug("AuthStatusMiddleware: Valid access token injected into Authorization header.")
            else:
                logger.info("AuthStatusMiddleware: Invalid/expired access token. Clearing Authorization header.")
                request.META.pop("HTTP_AUTHORIZATION", None)
        else:
            logger.debug("AuthStatusMiddleware: No access token found. Ensuring Authorization header is clear.")
            request.META.pop("HTTP_AUTHORIZATION", None)

        return None # Continue processing the request