# shiftmanagement/urls.py

from django.urls import path
from . import views

app_name = 'shiftmanagement'

urlpatterns = [
    path('calendar/', views.shift_calendar_view, name='shift_calendar'),
]