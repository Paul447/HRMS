from django.urls import path
from .views import  PTOBalanceView

urlpatterns = [
    path('ptobalance/', PTOBalanceView.as_view(), name='ptobalance'),
]
