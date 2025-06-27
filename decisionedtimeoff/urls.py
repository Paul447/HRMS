from .views import DecisionedTimeOffViewSetFrontend
from django.urls import path

urlpatterns = [path("", DecisionedTimeOffViewSetFrontend.as_view(), name="decisioned-timeoff")]