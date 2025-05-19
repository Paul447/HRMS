from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, TokenError, RefreshToken
from django.shortcuts import redirect
from django.urls import reverse

class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("hjjlzz_avrlu")
        refresh_token = request.COOKIES.get("ylmylzo_avrlu")
        login_path = reverse('frontend_login')
        if access_token:
            try:
                AccessToken(access_token)  # validate token
                # Inject Authorization header for DRF JWT auth classes
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            except TokenError:
                pass  # token invalid or expired, client should refresh explicitly
        if refresh_token:
            try: 
                RefreshToken(refresh_token)  # validate token

                if request.path == login_path:
                    # Redirect to the protected resource if already logged in
                    return redirect('/api/')
            except TokenError:
                pass  # token invalid or expired, client should refresh explicitly