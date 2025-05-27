from django.urls import path
from .views import PTORequestsView , TimeoffDetailsView

urlpatterns = [
    path('', PTORequestsView.as_view(), name='ptorequest'),
    path('details/', TimeoffDetailsView.as_view(), name='timeoff_details'),
]