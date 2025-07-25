from .views import DecisionedTimeOffViewSetFrontend
from django.urls import path


app_name = "hrmsauth"

urlpatterns = [path("", DecisionedTimeOffViewSetFrontend.as_view(), name="decisioned-timeoff")]