from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("hjjlzz_avrlu")
        refresh_token = request.COOKIES.get("ylmylzo_avrlu")
        login_path = reverse('frontend_login')

        if access_token:
            try:
                AccessToken(access_token)  # Validate token
                # Inject Authorization header for DRF JWT auth classes
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            except TokenError:
                pass  # Token invalid or expired, client should refresh explicitly

        if refresh_token:
            refresh_url = request.build_absolute_uri('/auth/api/token/refresh/')
            try:
                refresh = RefreshToken(refresh_token)  # Validate token
                new_access_token = str(refresh.access_token)
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"
                request._new_access_token = new_access_token
                if request.path == login_path:
                    # Redirect to the protected resource if already logged in
                    return redirect('/auth/dashboard/')
            except TokenError:
                pass  # Token invalid or expired, client should refresh explicitly

    def process_response(self, request, response):
        new_access_token = getattr(request, "_new_access_token", None)
        if new_access_token:
            response.set_cookie(
                "hjjlzz_avrlu",
                new_access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                max_age=900,  # 15 minutes
                path="/",
            )
        return response