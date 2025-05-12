from django.shortcuts import render
from .serializer import PayFrequencySerializer, UserSerializer,  GroupSerializer
from rest_framework import viewsets, serializers
from .models import pay_frequency
from django.contrib.auth.models import User , Permission, Group
from rest_framework.permissions import IsAuthenticated ,IsAdminUser, IsAuthenticatedOrReadOnly 

# Create your views here.

class PayFrequencyViewSet(viewsets.ModelViewSet):
    queryset = pay_frequency.objects.all()
    serializer_class = PayFrequencySerializer
    # permission_classes = [IsAdminUser]


    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class UserViewSet(viewsets.ModelViewSet):
    user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    queryset = User.objects.all()
    serializer_class = UserSerializer


