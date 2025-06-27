from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
import logging

from . import token_utils
from . import cookie_utils

logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(MiddlewareMixin):
    """
    Handles refreshing JWT access and refresh tokens if they are expired
    or missing. Sets new tokens as HTTP-only cookies on the response.
    Redirects to login if refresh token is invalid.
    """

    def process_response(self, request, response):
        access_token_from_cookie = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        login_url = reverse("frontend_login")

        # Determine if access token needs refreshing
        needs_refresh = False
        if not access_token_from_cookie:
            logger.debug("TokenRefreshMiddleware: Access token missing from cookie. Refresh might be needed.")
            needs_refresh = True
        elif not token_utils.verify_access_token(access_token_from_cookie):
            logger.info("TokenRefreshMiddleware: Access token expired/invalid. Attempting refresh.")
            needs_refresh = True
        else:
            logger.debug("TokenRefreshMiddleware: Access token is still valid. No refresh needed.")

        # Attempt to refresh token if needed and a refresh token exists
        if refresh_token and needs_refresh:
            new_access_token, new_refresh_token_rotated, error = token_utils.refresh_access_token(refresh_token)

            if new_access_token:
                # Flag to check if the original request was a GET for an HTML page that got 401
                was_html_get_401 = request.method == "GET" and response.status_code == 401 and "text/html" in request.META.get("HTTP_ACCEPT", "")

                final_response = response
                if was_html_get_401:
                    logger.info(f"TokenRefreshMiddleware: HTML GET request to {request.path} received 401. Refreshing token and redirecting.")
                    final_response = HttpResponseRedirect(request.path)
                    # Copy over any other cookies from the original response (e.g., CSRF token)
                    cookie_utils.copy_cookies_to_response(response, final_response)

                # Set the new tokens as cookies
                cookie_utils.set_jwt_cookies(final_response, new_access_token, new_refresh_token_rotated)
                logger.info("TokenRefreshMiddleware: New access/refresh tokens set in cookies.")

                if was_html_get_401:
                    return final_response  # Return the redirect response immediately

            else:  # Refresh token operation failed
                logger.warning(f"TokenRefreshMiddleware: Failed to refresh token: {error}. Clearing cookies and initiating login flow.")
                cookie_utils.delete_jwt_cookies(response)  # Clear cookies on the original response

                # If it was an HTML request, redirect to login page
                if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                    redirect_response = HttpResponseRedirect(login_url)
                    # Transfer cookie deletions to the new redirect response
                    cookie_utils.copy_cookies_to_response(response, redirect_response)
                    return redirect_response

        return response  # Return the original response (potentially with new cookies)
