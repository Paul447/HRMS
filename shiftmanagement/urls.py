# shiftmanagement/urls.py

from django.urls import path
from . import views

app_name = 'shiftmanagement'

urlpatterns = [
    path('calendar/', views.ShiftCalendarView.as_view(), name='shift_calendar_view'),
]