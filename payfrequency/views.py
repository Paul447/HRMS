from django.shortcuts import render
from .serializer import PayFrequencySerializer
from rest_framework import viewsets 
from .models import PayFrequency
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class PayFrequencyViewSet(viewsets.ModelViewSet):
    queryset = PayFrequency.objects.all()
    serializer_class = PayFrequencySerializer
    permission_classes = [IsAuthenticated]
