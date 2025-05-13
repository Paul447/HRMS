from django.shortcuts import render
from .serializer import AccuralRateSerializer
from .models import AccrualRates
from rest_framework import viewsets , serializers


# Create your views here.


class AccuralRateViewSet(viewsets.ModelViewSet):
    queryset = AccrualRates.objects.all()
    serializer_class = AccuralRateSerializer



