from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, TokenError, RefreshToken
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Retrieve JWT tokens from cookies
        access_token = request.COOKIES.get("hjjlzz_avrlu")
        refresh_token = request.COOKIES.get("ylmylzo_avrlu")
        
        # Get URL paths for login and logout
        login_path = reverse('frontend_login')
        log_out_path = reverse('logout')
        
        # Handle logout request: clear cookies and redirect to login
        if request.path == log_out_path:
            pass # No action needed, logout view will handle cookie clearing
        
        # If access token exists, try to validate it
        if access_token:
            try:
                AccessToken(access_token)  # Validate token (raises TokenError if invalid/expired)
                # Inject Authorization header so DRF can authenticate this request
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            except TokenError:
                # Access token invalid or expired; no action here, client should handle refresh
                pass
        
        # If access token is invalid/expired but refresh token exists, try to refresh access token
        if refresh_token and not access_token:
            try: 
                refresh = RefreshToken(refresh_token)  # Validate refresh token
                new_access_token = str(refresh.access_token)  # Generate new access token
                
                # Set new access token in Authorization header for current request
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"
                
                # Store the new access token to set it in response cookie later
                request._new_access_token = new_access_token
                
                # If user tries to access login page but is already authenticated, redirect to dashboard
            except TokenError:
                # Refresh token invalid or expired; user must log in again
                pass


        if access_token or refresh_token:
            # User is authenticated, redirect to dashboard if trying to access login page
            if request.path == login_path:
                return redirect('/auth/dashboard/')

    def process_response(self, request, response):
        # If a new access token was generated during the request, update the cookie in the response
        new_access_token = getattr(request, "_new_access_token", None)
        if new_access_token:
            response.set_cookie(
                "hjjlzz_avrlu",
                new_access_token,
                httponly=True,           # Prevent JS access to cookie
                secure=not settings.DEBUG,  # Use secure cookies in production
                samesite="Lax",          # CSRF protection setting
                max_age=900,             # 15 minutes expiration
                path="/",
            )
        return response
