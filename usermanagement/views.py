from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .serializer import ChangePasswordSerializer # Import your serializer

class ChangePasswordView(APIView):
    """
    An API endpoint for changing a user's password.
    Requires user to be authenticated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            
            user.set_password(new_password)
            user.save()

            # Optional: Invalidate all other sessions for the user to enhance security
            # This is a good practice after a password change.
            # Requires 'django.contrib.sessions' to be in INSTALLED_APPS
            # and 'django.contrib.auth.middleware.SessionAuthenticationMiddleware' for older Django versions.
            # For newer Django, check if the session hash changes on password change.
            # user.update_session_auth_hash(request) # This is for session authentication

            return Response(
                {"detail": "Password updated successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def change_password_template_view(request):
    """
    Renders the change password HTML template.
    Requires the user to be logged in.
    """
    return render(request, 'change_password.html')
