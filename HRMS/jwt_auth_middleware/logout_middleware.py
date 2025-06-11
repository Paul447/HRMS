from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
import logging

from . import token_utils
from . import cookie_utils

logger = logging.getLogger(__name__)

class LogoutMiddleware(MiddlewareMixin):
    """
    Specifically handles the logout path by blacklisting the refresh token
    and deleting all JWT-related cookies, then redirecting to the login page.
    This middleware should be placed early in the MIDDLEWARE list.
    """

    def process_request(self, request):
        # We process logout primarily in process_response, but we ensure the
        # Authorization header is cleared for the logout view itself.
        if request.path == reverse('logout'):
            logger.debug("LogoutMiddleware: Logout path requested in process_request. Clearing Authorization header.")
            request.META.pop("HTTP_AUTHORIZATION", None)
        return None # Let the request continue to the logout view

    def process_response(self, request, response):
        if request.path == reverse('logout'):
            refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
            login_url = reverse('frontend_login')

            logger.info("LogoutMiddleware: Handling logout request.")
            token_utils.blacklist_refresh_token(refresh_token)
            
            logout_response = HttpResponseRedirect(login_url)
            cookie_utils.delete_jwt_cookies(logout_response)
            logger.info("LogoutMiddleware: JWT cookies cleared and redirecting to login.")
            return logout_response
        
        return response