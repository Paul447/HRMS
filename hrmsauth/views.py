# views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, TokenError


# from .serializer import (
#     UserSerializer,
#     GroupSerializer,
#     UserRegisterPermissionSerializer,
#     UserRegisterGroupSerializer,
# )

import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Constants
# -----------------------------

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": not settings.DEBUG,  # Enable HTTPS-only cookies in production
    "samesite": "Lax",
    "path": "/",
}

# -----------------------------
# JWT Login View
# -----------------------------

class TokenObtainPairView(TokenObtainPairView):
    """
    Custom login view using SimpleJWT.
    Stores access and refresh tokens in HttpOnly cookies.
    """
    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            access = serializer.validated_data.get("access")
            refresh = serializer.validated_data.get("refresh")
            response = redirect("/auth/dashboard/")

            # Set cookies
            response.set_cookie("hjjlzz_avrlu", access, **COOKIE_SETTINGS, max_age=900)       # 15 min
            response.set_cookie("ylmylzo_avrlu", refresh, **COOKIE_SETTINGS, max_age=604800)  # 7 days
            return response
        except Exception:
            messages.error(request, "Invalid username or password.")
            return redirect("/auth/login/")

# -----------------------------
# JWT Refresh Token View
# -----------------------------

class RefreshTokenView(TokenRefreshView):
    """
    This view is not used till now. It is going to removed soon.
    """
    pass


# -----------------------------
# Logout View
# -----------------------------
@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    """
    Everything in this view is handled by the middleware. This is just a placeholder. Used for the logout URL.
    """
    pass 

# -----------------------------
# Permissions
# -----------------------------

class IsSuperUser(BasePermission):
    """
    Custom permission class that allows access only to superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser




# -----------------------------
# User Registration APIViews
# -----------------------------

@method_decorator(ensure_csrf_cookie, name='dispatch')
class FrontendLoginView(APIView):
    def get(self, request):
        return render(request, "login.html")

# @method_decorator(ensure_csrf_cookie, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)

        if not access_token:
            return redirect(reverse('frontend_login'))

        try:
            AccessToken(access_token).verify()
        except TokenError:
            return redirect(reverse('frontend_login'))

        return super().dispatch(request, *args, **kwargs)

