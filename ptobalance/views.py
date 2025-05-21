from rest_framework import viewsets
from .models import PTOBalance
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from .serializer import PTOBalanaceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render
# Create your views here.

class PTOBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PTOBalanaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PTOBalance.objects.filter(user=user)


class PTOBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'ptobalance_view.html')    