from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken, TokenError

class JWTAuthFromCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")
        if access_token:
            try:
                AccessToken(access_token)  # validate token
                # Inject Authorization header for DRF JWT auth classes
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            except TokenError:
                pass  # token invalid or expired, client should refresh explicitly
