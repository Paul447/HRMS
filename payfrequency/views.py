from django.shortcuts import render
from .serializer import PayFrequencySerializer
from rest_framework import viewsets 
from .models import pay_frequency
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class PayFrequencyViewSet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'message': 'You are authenticated Subesh '})  
    

def login_page(request):
    return render(request, 'login.html')

def dashboard(request): 
    perminsion_classes = [IsAuthenticated]
    return render(request, 'dashboard.html')