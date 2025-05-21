from django.urls import path
from .views import PTORequestsView

urlpatterns = [
    path('ptorequest/', PTORequestsView.as_view(), name='ptorequest'),
]