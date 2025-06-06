"""
URL configuration for HRMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from hrmsauth.views import *
from ptobalance.api import register as register_ptobalance
from ptorequest.api import register as register_ptorequest
from department.api import register_userprofile as register_userprofile
from paytype.api import register_department as register_department  
from hrmsauth.views import user_info
from punchreport.views import ClockDataViewSet
# from django.contrib.auth import views as auth_views
from drf_spectacular.views import SpectacularSwaggerView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()

router.register(r'clock', ClockDataViewSet, basename='clock')


register_department(router)

register_userprofile(router)



register_ptorequest(router)

register_ptobalance(router)





urlpatterns = [
    path('auth/', include('hrmsauth.url')),
    path('auth/ptobalance/', include('ptobalance.url')),
    path('auth/ptorequest/', include('ptorequest.url')),
    path('auth/clock/', include('timeclock.url')),
    path('auth/punchreport/', include('punchreport.url')),

    path('api/', include(router.urls)),
    path('api/user_info/', user_info, name='user_info'),
    path('admin/', admin.site.urls),
    path('api/clock/', include('timeclock.api')),  # API for time clock functionality
    

    
    # Yaml schema generation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Optional: Swagger UI
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Optional: ReDoc UI
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Need to generate the documentation of apiendpoints

]
