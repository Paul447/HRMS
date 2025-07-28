# views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import status
from department.models import UserProfile
from rest_framework.request import Request
from django.http import HttpResponse, HttpRequest 
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.renderers import TemplateHTMLRenderer
from .throttles import LoginRateThrottle
from rest_framework.permissions import IsAuthenticated
from .permissions import IsUnauthenticated
from rest_framework.exceptions import NotAuthenticated


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

COOKIE_SETTINGS = {"httponly": True, "secure": not settings.DEBUG, "samesite": "Lax", "path": "/"}  # Enable HTTPS-only cookies in production

# -----------------------------
# JWT Login View
# -----------------------------




class TokenObtainPairView(TokenObtainPairView):
    """
    Custom login view using SimpleJWT.
    Stores access and refresh tokens in HttpOnly cookies.
    Applies login throttling.
    """
    permission_classes = [IsUnauthenticated]  # Ensure only unauthenticated users can access this view
    throttle_classes = [LoginRateThrottle]
    versioning_class = None  # Disable versioning for this view 

    @method_decorator(csrf_protect, name="dispatch")
    def post(self, request, *args, **kwargs):
        # Check throttling before processing login
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                logger.warning(f"Throttled login attempt from IP: {request.META.get('REMOTE_ADDR')}")
                self.throttled(request, throttle.wait())

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            access = serializer.validated_data.get("access")
            refresh = serializer.validated_data.get("refresh")

            response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            response.set_cookie("hjjlzz_avrlu", access, **COOKIE_SETTINGS, max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())      # 15 minutes
            response.set_cookie("ylmylzo_avrlu", refresh, **COOKIE_SETTINGS, max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()) # 7 days

            return response

        except Exception as e:
            logger.info(f"Failed login attempt: {str(e)} from IP: {request.META.get('REMOTE_ADDR')}")
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )


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
@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    versioning_class = None  # Disable versioning for this view
    """
    Everything in this view is handled by the middleware. This is just a placeholder. Used for the logout URL.
    """

    pass



class UserInfoViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):  # routers use `list` for GET /user-info/
        user = request.user
        user_profile = UserProfile.objects.filter(user=user).first()
        return Response({"id": user.id, "username": user.username, "is_authenticated": user.is_authenticated, "is_superuser": user.is_superuser, "is_time_off": user_profile.is_time_off if user_profile else False, "is_manager": user_profile.is_manager if user_profile else False, "name": user_profile.department.name})


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


@method_decorator(ensure_csrf_cookie, name="dispatch")
class FrontendLoginView(APIView):
    versioning_class = None
    def get(self, request: Request) -> HttpResponse:
        try:
            return render(request, "login.html")
        except Exception as e:
            # Optional: Log the error if needed
            return Response({"error": "Unable to load login page"}, status=500)


# @method_decorator(ensure_csrf_cookie, name='dispatch')
class DashboardView(APIView):
    versioning_class = None
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "dashboard.html"
    login_url = "hrmsauth:frontend_login"  # Django URL name

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)