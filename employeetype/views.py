from django.shortcuts import render
from rest_framework import serializers, viewsets
from .models import EmployeeType
from .serializer import EmployeeTypeSerializer


# Create your views here.
class EmployeeTypeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeSerializer
