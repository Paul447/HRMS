from django.shortcuts import render
from rest_framework import viewsets
from .models import Department, UserProfile
from .serializer import DepartmentSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return UserProfile.objects.filter(user=user)
