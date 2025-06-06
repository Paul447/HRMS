# urls.py
from django.urls import path
from .views import UserClockDataFrontendView

urlpatterns = [
    path('clock-in-out-view/', UserClockDataFrontendView.as_view(), name='clock_in_out'),
]