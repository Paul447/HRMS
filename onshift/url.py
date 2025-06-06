# urls.py
from django.urls import path
from .views import  OnShiftFrontendView

urlpatterns = [
    path('on-shift-details/', OnShiftFrontendView.as_view(), name='on_shift_report'),
]