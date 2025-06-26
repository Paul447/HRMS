from django.urls import path
from .views import TimeOffBalanceTemplate

urlpatterns = [
    path('', TimeOffBalanceTemplate.as_view(), name='time_off_balance_template'),
]