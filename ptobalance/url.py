from django.urls import path
from .views import  PTOBalanceView

urlpatterns = [
    path('', PTOBalanceView.as_view(), name='ptobalance'),
]
