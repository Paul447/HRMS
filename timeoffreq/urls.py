from django.urls import path
from .views import TimeOffRequestView,TimeOffRequestDetailsView

urlpatterns = [
    path('', TimeOffRequestView.as_view(), name='timeoff_request'),
    path('view/', TimeOffRequestDetailsView.as_view(), name='timeoff_request_view'),
]