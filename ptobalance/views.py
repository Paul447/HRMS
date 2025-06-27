from rest_framework import viewsets
from .models import PTOBalance
from .serializer import PTOBalanceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.shortcuts import redirect
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class PTOBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PTOBalanceSerializer

    def get_queryset(self):
        user = self.request.user
        return PTOBalance.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "PTO balance not found."}, status=404)

        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


class PTOBalanceView(TemplateView, LoginRequiredMixin):
    template_name = "ptobalance_view.html"
    login_url = "frontend_login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
