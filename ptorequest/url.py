from django.urls import path
from .views import PTORequestsView , TimeoffDetailsView, GetPastPTORequestsView

urlpatterns = [
    path('', PTORequestsView.as_view(), name='ptorequest'),
    path('details/', TimeoffDetailsView.as_view(), name='timeoff_details'),
    path('past-requests/', GetPastPTORequestsView.as_view(), name='past_ptorequests'),
]