from django.urls import path
from .views import TimeOffRequestView

urlpatterns = [
    path('', TimeOffRequestView.as_view(), name='timeoff_request'),
]