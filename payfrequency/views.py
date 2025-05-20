from django.shortcuts import render
from .serializer import PayFrequencySerializer
from rest_framework import viewsets
from .models import Pay_Frequency
from rest_framework.permissions import IsAdminUser  

# Create your views here.

class PayFrequencyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Pay_Frequency.objects.all()
    serializer_class = PayFrequencySerializer



