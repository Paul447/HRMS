from django.urls import path
from .views import TimeOffBalanceTemplate

app_name = "timeoffbalance"

urlpatterns = [path("", TimeOffBalanceTemplate.as_view(), name="time_off_balance_template")]
