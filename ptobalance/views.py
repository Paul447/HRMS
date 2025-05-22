from rest_framework import viewsets
from .models import PTOBalance
from .serializer import PTOBalanaceSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.shortcuts import redirect

# Create your views here.

class PTOBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PTOBalanaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PTOBalance.objects.filter(user=user)


class PTOBalanceView(TemplateView):
    template_name = 'ptobalance.html'
    def dispatch(self, request, *args, **kwargs):
        access_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)

        if not access_token:
            return redirect(reverse('frontend_login'))

        try:
            AccessToken(access_token).verify()
        except TokenError:
            return redirect(reverse('frontend_login'))

        return super().dispatch(request, *args, **kwargs)
