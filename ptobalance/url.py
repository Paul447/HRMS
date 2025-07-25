from django.urls import path
from .views import PTOBalanceView

app_name = "ptobalance"
urlpatterns = [path("", PTOBalanceView.as_view(), name="ptobalance")]
