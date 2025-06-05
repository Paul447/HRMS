# urls.py
from django.urls import path
from .views import ClockInOutAPIView, UserClockDataAPIView, CurrentPayPeriodAPIView, UserClockOnShiftView

urlpatterns = [
    # API for clocking in/out
    path('clock-in-out/', ClockInOutAPIView.as_view(), name='api_clock_in_out'),
    
    # API for getting user's clock data (status, entries, weekly hours)
    path('user-clock-data/', UserClockDataAPIView.as_view(), name='api_user_clock_data'),

    # API for getting the current pay period details
    path('current-pay-period/', CurrentPayPeriodAPIView.as_view(), name='api_current_pay_period'),

    path('on-shift/', UserClockOnShiftView.as_view(), name='api_user_clock_on_shift'),
    
    # You will also need to include DRF's authentication URLs if using session authentication
    # path('/api-auth/', include('rest_framework.urls')),
]