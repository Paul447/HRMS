from django.urls import path
from .views import PTORequestsView

urlpatterns = [
    path('', PTORequestsView.as_view(), name='ptorequest'),
]