from django.shortcuts import render
from .serializer import PayFrequencySerializer, UserSerializer,  GroupSerializer
from rest_framework import viewsets, serializers
from .models import Pay_Frequency
from django.contrib.auth.models import User , Permission, Group
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, BasePermission

# Create your views here.

class PayFrequencyViewSet(viewsets.ModelViewSet):
    queryset = Pay_Frequency.objects.all()
    serializer_class = PayFrequencySerializer
    # permission_classes = [IsAdminUser]
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


