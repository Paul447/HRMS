from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": not settings.DEBUG,  # HTTPS in production only 
    "samesite": "Lax",
    "path": "/",
}
import logging
logger = logging.getLogger(__name__)

class LoginView(TokenObtainPairView):
    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            access = serializer.validated_data.get("access")
            refresh = serializer.validated_data.get("refresh")
            response = redirect("/api/")
            response.set_cookie("access_token", access, **COOKIE_SETTINGS , max_age=900)
            response.set_cookie("refresh_token", refresh, **COOKIE_SETTINGS, max_age=604800)
            return response
        except Exception:
            messages.error(request, "Invalid username or password.")
            return redirect("/auth/login/")





class RefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token not found"}, status=401)

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            data = response.data
            new_access = data.get("access")
            new_refresh = data.get("refresh")

            response.set_cookie("access_token", new_access, **COOKIE_SETTINGS)
            if new_refresh:
                response.set_cookie("refresh_token", new_refresh, **COOKIE_SETTINGS)
            response.data = {"detail": "Token refreshed"}
        return response

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, you're authenticated!"})

@method_decorator(ensure_csrf_cookie, name='dispatch')
class FrontendLoginView(APIView):
    def get(self, request):
        return render(request, "login.html")
