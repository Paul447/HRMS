from django.shortcuts import render
from .serializer import PayFrequencySerializer
from rest_framework import viewsets
from .models import Pay_Frequency


# Create your views here.

class PayFrequencyViewSet(viewsets.ModelViewSet):
    queryset = Pay_Frequency.objects.all()
    serializer_class = PayFrequencySerializer
    # permission_classes = [IsAdminUser]



