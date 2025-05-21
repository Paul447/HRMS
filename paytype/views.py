from django.shortcuts import render
from rest_framework import viewsets 
from .models import PayType

from .serializer import PayTypeSerializer
from rest_framework.permissions import IsAuthenticated

class PayTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = PayType.objects.all()

# Create your views here.
