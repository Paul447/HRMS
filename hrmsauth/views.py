# views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render

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

class LoginView(TokenObtainPairView):
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
    Refreshes JWT token using refresh token from cookies.
    Returns only a success message instead of the tokens.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("ylmylzo_avrlu")
        if not refresh_token:
            return Response({"detail": "Refresh token not found"}, status=401)

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            new_access = response.data.get("access")
            new_refresh = response.data.get("refresh")

            # Set new access token
            response.set_cookie("hjjlzz_avrlu", new_access, **COOKIE_SETTINGS, max_age=900)

            # Set new refresh token if returned
            if new_refresh:
                response.set_cookie("ylmylzo_avrlu", new_refresh, **COOKIE_SETTINGS, max_age=86400)

            # Hide actual token values from frontend
            response.data = {"detail": "Token refreshed"}

        return response

# -----------------------------
# Logout View
# -----------------------------
@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    """
    Logs out the user by deleting authentication cookies.
    """
    permission_classes = [IsAuthenticated]

       
    def post(self, request):
        response = redirect("/auth/login/")
        response.delete_cookie("hjjlzz_avrlu", path="/")
        response.delete_cookie("ylmylzo_avrlu", path="/")
        return response

# -----------------------------
# Protected Test View
# -----------------------------

class ProtectedView(APIView):
    """
    Sample protected API view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, you're authenticated!"})

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
# ViewSets for Group, Permission, and User
# -----------------------------

# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     CRUD operations for Django's built-in Group model.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


# class UserRegisterPermissionViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Allows listing and managing available permissions
#     (for use when assigning to users or groups).
#     """
#     permission_classes = [IsAuthenticated, IsSuperUser]
#     queryset = Permission.objects.all()
#     serializer_class = UserRegisterPermissionSerializer


# class UserRegisterGroupViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     Allows listing and managing available groups
#     (for use when assigning to users).
#     """
#     permission_classes = [IsAuthenticated, IsSuperUser]
#     queryset = Group.objects.all()
#     serializer_class = UserRegisterGroupSerializer

    
# @method_decorator(csrf_protect, name='dispatch')
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     Full CRUD for the User model. Requires superuser access.
#     Uses a custom serializer that includes password logic,
#     group and permission assignment, and validation.
#     """
#     # permission_classes = [IsAuthenticated, IsSuperUser]
#     queryset = User.objects.all()
#     serializer_class = UserSerializer















@method_decorator(ensure_csrf_cookie, name='dispatch')
class FrontendLoginView(APIView):
    def get(self, request):
        return render(request, "login.html")

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, "dashboard.html")
class RegisterUserView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get(self, request):
        return render(request, "register.html")
class ViewUsersView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get(self, request):
        return render(request, "viewuser.html")
class EditUserView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        return render(request, "edituser.html", {"user": user})