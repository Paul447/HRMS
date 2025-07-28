from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
import logging

from . import token_utils
from . import cookie_utils

logger = logging.getLogger(__name__)

class LogoutMiddleware(MiddlewareMixin):
    """
    Handles the logout path by blacklisting the refresh token and deleting JWT cookies.
    Redirects to the login page.
    """

    def process_request(self, request):
        if request.path == reverse("hrmsauth:logout"):
            logger.debug("Logout path requested. Clearing Authorization header.")
            request.META.pop("HTTP_AUTHORIZATION", None)
        return None

    def process_response(self, request, response):
        if request.path == reverse("hrmsauth:logout"):
            refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
            login_url = reverse("hrmsauth:frontend_login")

            # Validate redirect URL
            if not url_has_allowed_host_and_scheme(login_url, allowed_hosts={request.get_host()}):
                logger.error("Invalid login redirect URL detected.")
                return response  # Return original response to avoid open redirects

            logger.info("Handling logout request.")
            token_utils.blacklist_refresh_token(refresh_token)
            logout_response = HttpResponseRedirect(login_url)
            cookie_utils.delete_jwt_cookies(logout_response)
            logger.info("JWT cookies cleared and redirecting to login.")
            return logout_response

        return response