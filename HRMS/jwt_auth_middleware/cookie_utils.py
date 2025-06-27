from django.conf import settings
from django.http import HttpResponse


def set_jwt_cookies(response: HttpResponse, access_token: str, refresh_token: str = None):
    """Sets the access and refresh token cookies on the response."""
    response.set_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, access_token, httponly=True, secure=not settings.DEBUG, samesite="Lax", max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(), path="/")
    if refresh_token:
        response.set_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, refresh_token, httponly=True, secure=not settings.DEBUG, samesite="Lax", max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(), path="/")


def delete_jwt_cookies(response: HttpResponse):
    """Deletes the access and refresh token cookies from the response."""
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME, path="/")
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME, path="/")


def copy_cookies_to_response(source_response: HttpResponse, destination_response: HttpResponse):
    """Copies all cookies from one HttpResponse to another."""
    for name, morsel in source_response.cookies.items():
        destination_response.cookies[name] = morsel
