# urls.py
from django.urls import path
from .views import ClockInOutAPIView, UserClockDataAPIView, CurrentPayPeriodAPIView, UserClockDataFrontendView

urlpatterns = [

    # View for clocking in/out
    path('clock-in-out-view/', UserClockDataFrontendView.as_view(), name='clock_in_out'),
    # You will also need to include DRF's authentication URLs if using session authentication
    # path('/api-auth/', include('rest_framework.urls')),
]