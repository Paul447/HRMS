# urls.py
from django.urls import path
from .views import ClockInOutAPIView, UserClockDataAPIView, CurrentPayPeriodAPIView, UserClockDataFrontendView, ClockInOutPunchReportView

urlpatterns = [

    # View for clocking in/out
    path('clock-in-out-view/', UserClockDataFrontendView.as_view(), name='clock_in_out'),
    path('clock-in-out-punch-report/', ClockInOutPunchReportView.as_view(), name='clock_in_out_punch_report'),
    # You will also need to include DRF's authentication URLs if using session authentication
    # path('/api-auth/', include('rest_framework.urls')),
]