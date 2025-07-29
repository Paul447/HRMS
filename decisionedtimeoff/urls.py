from .views import DecisionedTimeOffViewSetFrontend
from django.urls import path


app_name = "decisioned_timeoff"

urlpatterns = [path("", DecisionedTimeOffViewSetFrontend.as_view(), name="decisioned-timeoff")]