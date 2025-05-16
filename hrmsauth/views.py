from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render

COOKIE_SETTINGS = {
    "httponly": True,
    "secure": True,
    "samesite": "Lax",
}

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response({"message": "Login successful"})
        response.set_cookie("access_token", access, **COOKIE_SETTINGS)
        response.set_cookie("refresh_token", str(refresh), **COOKIE_SETTINGS)
        return response

class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, you're authenticated!"})

class FrontendLoginView(APIView):
    def get(self, request):
        return render(request, "login.html")
