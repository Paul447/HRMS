from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, TokenError, RefreshToken
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    """
    Handles JWT authentication via HTTP-only cookies.
    It injects access tokens, refreshes them when expired,
    and manages logout.
    """

    def process_request(self, request):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        
        login_url = reverse('frontend_login') # Your login page URL
        dashboard_url = reverse('dashboard')  # Your dashboard URL

        # Scenario 1: User tries to log out
        if request.path == reverse('logout'):
            logger.debug("Logout path requested. Bypassing token processing.")
            request.META.pop("HTTP_AUTHORIZATION", None) # Clear header before logout view
            return None # Let the logout view handle the response

        # Scenario 2: Authenticated user tries to access the login page
        if access_token and request.path == login_url:
            try:
                AccessToken(access_token).verify() # Check if token is still valid
                logger.debug("Authenticated user on login page. Redirecting to dashboard.")
                return redirect(dashboard_url) # Send them to dashboard if already logged in
            except TokenError:
                logger.debug("Expired/invalid access token on login page. Allowing access.")
                request.META.pop("HTTP_AUTHORIZATION", None) # Clear header if token is bad

        # Scenario 3: Regular request with a potential access token
        if access_token:
            try:
                AccessToken(access_token).verify()
                # If valid, inject into header for DRF
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                logger.debug("Valid access token injected into Authorization header.")
            except TokenError as e:
                # If expired or invalid, remove header to force DRF to treat as unauthenticated
                logger.info(f"Invalid/expired access token: {e}. Clearing Authorization header.")
                request.META.pop("HTTP_AUTHORIZATION", None)
        else:
            # No access token at all, ensure header is clear
            logger.debug("No access token found. Ensuring Authorization header is clear.")
            request.META.pop("HTTP_AUTHORIZATION", None)

        return None # Continue processing the request to the view

    def process_response(self, request, response):
        access_token_from_cookie = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        login_url = reverse('frontend_login')

        # Scenario 1: Handling logout
        if request.path == reverse('logout'):
            logger.info("Clearing JWT cookies on logout.")
            try:
                if refresh_token: # Only try to blacklist if a token exists
                    RefreshToken(refresh_token).blacklist()
            except Exception as e:
                logger.warning(f"Refresh token blacklist error on logout: {e}")
            
            # Create a redirect response to the login page and delete cookies
            logout_response = HttpResponseRedirect(login_url)
            logout_response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/")
            logout_response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/")
            return logout_response

        # Determine if access token needs refreshing
        needs_refresh = False
        if not access_token_from_cookie:
            logger.debug("Access token missing from cookie. Refresh might be needed.")
            needs_refresh = True
        else:
            try:
                AccessToken(access_token_from_cookie).verify()
                logger.debug("Access token is still valid. No refresh needed.")
            except TokenError:
                logger.info("Access token expired/invalid. Attempting refresh.")
                needs_refresh = True

        # Scenario 2: Attempt to refresh token if needed and refresh token exists
        if refresh_token and needs_refresh:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)

                # Flag to check if the original request was a GET for an HTML page that got 401
                was_html_get_401 = (
                    request.method == 'GET' and
                    response.status_code == 401 and
                    'text/html' in request.META.get('HTTP_ACCEPT', '')
                )

                # Prepare the response object for setting cookies.
                # If it was an HTML GET 401, we'll create a redirect response.
                # Otherwise, we'll modify the original response.
                final_response = response
                if was_html_get_401:
                    logger.info(f"HTML GET request to {request.path} received 401. Refreshing token and redirecting.")
                    final_response = HttpResponseRedirect(request.path)
                    # Copy over any other cookies (like CSRF) from the original response
                    for name, morsel in response.cookies.items():
                        final_response.cookies[name] = morsel

                # Set the new access token cookie
                final_response.set_cookie(
                    settings.ACCESS_TOKEN_COOKIE_NAME,
                    new_access_token,
                    httponly=True,
                    secure=not settings.DEBUG, # Use secure in production
                    samesite="Lax",
                    max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                    path="/",
                )
                logger.info("Access token refreshed and set in cookie.")

                # Handle refresh token rotation if enabled
                if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                    User = get_user_model()
                    user_id = refresh['user_id']
                    try:
                        user = User.objects.get(id=user_id)
                        new_refresh_token = str(RefreshToken.for_user(user))
                        
                        # Blacklist old refresh token if setting is enabled
                        if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION', False):
                            refresh.blacklist()
                            logger.debug("Old refresh token blacklisted.")
                        
                        final_response.set_cookie(
                            settings.REFRESH_TOKEN_COOKIE_NAME,
                            new_refresh_token,
                            httponly=True,
                            secure=not settings.DEBUG,
                            samesite="Lax",
                            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                            path="/",
                        )
                        logger.info("Refresh token rotated and set in cookie.")
                    except User.DoesNotExist:
                        logger.warning(f"User with ID {user_id} not found during refresh rotation. Invalidate session.")
                        # If user doesn't exist, tokens are useless. Clear and redirect to login.
                        final_response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/")
                        final_response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/")
                        if was_html_get_401:
                            final_response = HttpResponseRedirect(login_url) # Redirect to login if a page load
                
                # If we performed an HTML GET 401 redirect, return it immediately
                if was_html_get_401:
                    return final_response

            except TokenError as e:
                logger.warning(f"Invalid refresh token: {e}. Clearing cookies and initiating login flow.")
                # Refresh token itself is bad, so clear both cookies
                response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/")
                response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/")
                
                # If it was an HTML request, redirect to login page
                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    redirect_response = HttpResponseRedirect(login_url)
                    # Transfer cookie deletions to the new redirect response
                    for name, morsel in response.cookies.items():
                        if morsel.key in [settings.ACCESS_TOKEN_COOKIE_NAME, settings.REFRESH_TOKEN_COOKIE_NAME]:
                            redirect_response.cookies[name] = morsel
                    return redirect_response
        
        return response # Return the original response (potentially with new cookies)