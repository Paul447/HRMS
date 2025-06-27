from django.urls import path
from .views import DepartmentTemplateView

urlpatterns = [path("department-leaves/", DepartmentTemplateView.as_view(), name="department_leaves_template")]
