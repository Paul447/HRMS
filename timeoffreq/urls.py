from django.urls import path
from .views import TimeOffRequestView, TimeOffRequestDetailsView, GetPastTimeOffRequestsView
app_name = "timeoffreq"

urlpatterns = [path("", TimeOffRequestView.as_view(), name="timeoff_request"), path("view/", TimeOffRequestDetailsView.as_view(), name="timeoff_request_view"), path("past-timeoff-requests/", GetPastTimeOffRequestsView.as_view(), name="past_timeoff_requests")]
