from django.shortcuts import render
from rest_framework import serializers, viewsets
from .models import BiweeklyCron
from .serializer import BiweeklyCronSerializer

class BiweeklyCronViewSet(viewsets.ModelViewSet):
    queryset = BiweeklyCron.objects.all()
    serializer_class = BiweeklyCronSerializer
    

# Create your views here.
