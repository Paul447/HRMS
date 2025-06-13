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
from department.api import register_userprofile as register_userprofile
from hrmsauth.views import UserInfoViewSet
from punchreport.views import PunchReportViewSet 
from payperiod.views import PayPeriodUptoTodayViewSet,PayPeriodViewSetForPastTimeOffRequest,PayPeriodViewSetForCurrentFutureTimeOffRequest
# from django.contrib.auth import views as auth_views
from drf_spectacular.views import SpectacularSwaggerView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from adminorganizer.admin.admin_site import hrms_admin_site
from timeclock.views import UserClockDataAPIView, ClockInOutCreate
from leavetype.views import DepartmentBasedLeaveTypeViewSet
from department.views import UserProfileViewSet
from ptorequest.views import PTORequestsViewSet , GetPTORequestsFromPastPayPeriodViewSet
from ptobalance.views import PTOBalanceViewSet
from onshift.views import UserClockOnShiftViewSet
from timeoff_management.views import DepartmentReturnView,TimeOffRequestViewCurrentPayPeriodAdmin
router = DefaultRouter()

# router.register(r'clock', ClockDataViewSet, basename='clock')
router.register(r'user_info', UserInfoViewSet, basename='user_info')
router.register(r'punch-report', PunchReportViewSet, basename='punch_report')
router.register(r'pay-period', PayPeriodUptoTodayViewSet, basename='pay_period_upto_today')
router.register(r'past-pay-period', PayPeriodViewSetForPastTimeOffRequest, basename='past_pay_period')
router.register(r'current-future-pay-period', PayPeriodViewSetForCurrentFutureTimeOffRequest, basename='current_future_pay_period')
router.register(r'departmentleavetype', DepartmentBasedLeaveTypeViewSet, basename='departmentleavetype')
router.register(r'department', UserProfileViewSet, basename='userprofile')
router.register(r'pto-requests', PTORequestsViewSet, basename='pto-requests')
router.register(r'past-pto-requests', GetPTORequestsFromPastPayPeriodViewSet, basename='past-ptorequests')
router.register(r'ptobalance',PTOBalanceViewSet, basename = 'ptobalance')
router.register(r'all-departments', DepartmentReturnView, basename='all_departments')
router.register(r'time-off-manage', TimeOffRequestViewCurrentPayPeriodAdmin, basename='time_off_requests')


clock_router = DefaultRouter()
clock_router.register(r'user-clock-data', UserClockDataAPIView, basename='clock_in_out_get')
clock_router.register(r'clock-in-out', ClockInOutCreate, basename='clock_in_out_post')
clock_router.register(r'on-shift', UserClockOnShiftViewSet, basename='on_shift')



urlpatterns = [


    # Auth Custom Admin Site URLS 
    path('auth/', include('hrmsauth.url')),
    path('auth/ptobalance/', include('ptobalance.url')),
    path('auth/ptorequest/', include('ptorequest.url')),
    path('auth/clock/', include('timeclock.url')),
    path('auth/punchreport/', include('punchreport.url')),
    path('auth/onshift/', include('onshift.url')),
    path('auth/timeoff/', include('timeoff_management.url')),

    path('api/', include(router.urls)),
    path('api/clock/', include(clock_router.urls)),  # API for clock functionality


    # Admin URLs
    path('admin/', hrms_admin_site.urls),

    # Yaml schema generation # Api Documentation Related URLS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),


]
