from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme


import logging

from . import token_utils
from . import cookie_utils

logger = logging.getLogger(__name__)

class TokenRefreshMiddleware(MiddlewareMixin):
    """
    Refreshes JWT access and refresh tokens if expired or missing.
    Sets new tokens as HTTP-only cookies and redirects to login if refresh fails.
    """


    def process_response(self, request, response):
        access_token_from_cookie = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        login_url = reverse("hrmsauth:frontend_login")

        # Validate redirect URL
        if not url_has_allowed_host_and_scheme(login_url, allowed_hosts={request.get_host()}):
            logger.error("Invalid login redirect URL detected.")
            return response

        needs_refresh = False
        if not access_token_from_cookie:
            logger.debug("Access token missing from cookie. Refresh needed.")
            needs_refresh = True
        elif not token_utils.verify_access_token(access_token_from_cookie):
            logger.info("Access token expired/invalid. Attempting refresh.")
            needs_refresh = True
        else:
            logger.debug("Access token is valid. No refresh needed.")

        if refresh_token and needs_refresh:
            new_access_token, new_refresh_token_rotated, error = token_utils.refresh_access_token(refresh_token)

            if new_access_token:
                was_html_get_401 = (
                    request.method == "GET"
                    and response.status_code == 401
                    and "text/html" in request.META.get("HTTP_ACCEPT", "")
                )
                final_response = response
                if was_html_get_401:
                    logger.info(f"HTML GET request to {request.path} received 401. Redirecting with new tokens.")
                    final_response = HttpResponseRedirect(request.path)
                    cookie_utils.copy_cookies_to_response(response, final_response)

                cookie_utils.set_jwt_cookies(final_response, new_access_token, new_refresh_token_rotated)
                logger.info("New access/refresh tokens set in cookies.")
                if was_html_get_401:
                    return final_response
            else:
                logger.warning(f"Failed to refresh token: {error}. Clearing cookies and redirecting to login.")
                cookie_utils.delete_jwt_cookies(response)
                if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                    redirect_response = HttpResponseRedirect(login_url)
                    cookie_utils.copy_cookies_to_response(response, redirect_response)
                    return redirect_response

        return response