from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import PTORequests
from .serializer import PTORequestsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render

class PTORequestsViewSet(viewsets.ModelViewSet):
    queryset = PTORequests.objects.all()
    serializer_class = PTORequestsSerializer
    permission_classes = [IsAuthenticated]
    

