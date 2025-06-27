from django.urls import path
from usermanagement.views import change_password_template_view

urlpatterns = [path('change-password/', change_password_template_view, name='change_password_template'),]