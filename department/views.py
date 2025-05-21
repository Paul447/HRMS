from django.shortcuts import render
from rest_framework import viewsets
from .models import Department
from .serializer import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()

# Create your views here.
