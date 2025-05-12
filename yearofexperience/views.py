from django.shortcuts import render
from .serializer import YearOfExperienceSerializer
from rest_framework import viewsets , serializers
from .models import YearOfExperience
from django.contrib.auth.models import User , Permission, Group


class YearOfExperienceViewSet(viewsets.ModelViewSet):
    queryset = YearOfExperience.objects.all()
    serializer_class = YearOfExperienceSerializer
    

# Create your views here.
