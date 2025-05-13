from rest_framework import viewsets
from .models import PTOBalance
from .serializer import PTOBalanaceSerializer
# Create your views here.

class PTOBalanceViewSet(viewsets.ModelViewSet):
    queryset = PTOBalance.objects.all()
    serializer_class = PTOBalanaceSerializer
