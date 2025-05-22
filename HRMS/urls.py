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
from yearofexperience.api import register as register_experience
from payfrequency.api import register as register_pay

from hrmsauth.views import *

from accuralrates.api import register as register_accuralrates
from employeetype.api import register as register_employeetypes
from ptobalance.api import register as register_ptobalance
from biweeklycron.api import register as register_biweeklycron
from ptorequest.api import register as register_ptorequest
from department.api import register as register_department
from paytype.api import register as register_paytype    
# from django.contrib.auth import views as auth_views
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()
register_experience(router)
register_pay(router)

register_paytype(router)
register_department(router)



register_ptorequest(router)
register_accuralrates(router)
register_employeetypes(router)
register_ptobalance(router)
register_biweeklycron(router)




urlpatterns = [
    path('auth/', include('hrmsauth.url')),
    path('auth/ptobalance/', include('ptobalance.url')),
    path('auth/ptorequest/', include('ptorequest.url')),
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),

    
    # Yaml schema generation
    # path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Need to generate the documentation of apiendpoints

]
