from django.urls import path
from .views import TimeOffTemplateView

urlpatterns = [path("time-off-manage/", TimeOffTemplateView.as_view(), name="timeoff_management_template")]
