# urls.py
from django.urls import path
from .views import ClockInOutAPIView, UserClockDataAPIView
urlpatterns = [
    # API for clocking in/out
    path('clock-in-out/', ClockInOutAPIView.as_view(), name='api_clock_in_out'),
    
    # API for getting user's clock data (status, entries, weekly hours)
    path('user-clock-data/', UserClockDataAPIView.as_view(), name='api_user_clock_data'),

]