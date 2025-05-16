import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        # Prevent login if already authenticated
        if request.path == "/auth/login/" and access_token:
            try:
                AccessToken(access_token)
                return JsonResponse({"detail": "Already logged in"}, status=400)
            except TokenError:
                pass  # Let them proceed to login if token invalid

        # Set Authorization header if access token is valid
        if access_token:
            try:
                AccessToken(access_token)
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
                return
            except TokenError:
                pass  # Access token expired or invalid

        # Try refreshing access token from refresh token
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"
                request._new_access_token = new_access_token
            except TokenError:
                logger.warning("Invalid refresh token in middleware")

    def process_response(self, request, response):
        new_access_token = getattr(request, "_new_access_token", None)
        if new_access_token:
            response.set_cookie(
                "access_token",
                new_access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
            )
        return response
