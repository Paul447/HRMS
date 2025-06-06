# urls.py
from django.urls import path
from .views import ClockInOutAPIView, UserClockDataAPIView, CurrentPayPeriodAPIView, UserClockOnShiftView

urlpatterns = [

    path('current-pay-period/', CurrentPayPeriodAPIView.as_view(), name='api_current_pay_period'),

    path('on-shift/', UserClockOnShiftView.as_view(), name='api_user_clock_on_shift'),
    
]