# urls.py
from django.urls import path
from .views import ClockInOutPunchReportView

urlpatterns = [
    path('clock-in-out-punch-report/', ClockInOutPunchReportView.as_view(), name='clock_in_out_punch_report'),
]