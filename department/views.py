from django.shortcuts import render
from rest_framework import viewsets
from .models import UserProfile
from .serializer import  UserProfileSerializer
from rest_framework.permissions import IsAuthenticated


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return UserProfile.objects.filter(user=user)
    
