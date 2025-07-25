# urls.py
from django.urls import path
from .views import OnShiftFrontendView

app_name = "onshift"

urlpatterns = [path("on-shift-details/", OnShiftFrontendView.as_view(), name="on_shift_report")]
