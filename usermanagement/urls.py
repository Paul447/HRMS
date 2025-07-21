from django.urls import path
from usermanagement.views import ChangePasswordTemplateAPIView

urlpatterns = [path('change-password/', ChangePasswordTemplateAPIView.as_view(), name='change_password_template'),]