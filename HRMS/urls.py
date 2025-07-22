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
from hrmsauth.views import UserInfoViewSet
from punchreport.views import PunchReportViewSet
from payperiod.views import PayPeriodUptoTodayViewSet, PayPeriodViewSetForPastTimeOffRequest, PayPeriodViewSetForCurrentFutureTimeOffRequest
from django.views.generic.base import RedirectView  # Import RedirectView

# from django.contrib.auth import views as auth_views
from drf_spectacular.views import SpectacularSwaggerView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from adminorganizer.admin.admin_site import hrms_admin_site
from timeclock.views import UserClockDataAPIView, ClockInOutCreate
from ptobalance.views import PTOBalanceViewSet
from deptleaves.views import DepartmentLeavesViewSet
from onshift.views import UserClockOnShiftViewSet
from notificationapp.views import NotificationViewSet
from timeoffreq.views import TimeoffRequestViewSetEmployee, DepartmentLeaveTypeDropdownView, PastTimeOffRequestViewSet
from timeoff_management.views import ManagerTimeoffApprovalViewSet
from usertimeoffbalance.views import TimeoffBalanceViewSet
from decisionedtimeoff.views import DecisionedTimeOffViewSet
from usermanagement.views import ChangePasswordView
from shiftmanagement.views import CalendarEventViewSet


# IMPORTS YOU NEED TO ADD:
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static file serving helper

router = DefaultRouter()

# router.register(r'clock', ClockDataViewSet, basename='clock')
router.register(r"user_info", UserInfoViewSet, basename="user_info")
router.register(r"punch-report", PunchReportViewSet, basename="punch_report")
router.register(r"pay-period", PayPeriodUptoTodayViewSet, basename="pay_period_upto_today")
router.register(r"past-pay-period", PayPeriodViewSetForPastTimeOffRequest, basename="past_pay_period")
router.register(r"current-future-pay-period", PayPeriodViewSetForCurrentFutureTimeOffRequest, basename="current_future_pay_period")
router.register(r"ptobalance", PTOBalanceViewSet, basename="ptobalance")
router.register(r"department-leaves", DepartmentLeavesViewSet, basename="department_leaves")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"timeoffrequests", TimeoffRequestViewSetEmployee, basename="timeoffrequests")
router.register(r"past-timeoff-requests", PastTimeOffRequestViewSet, basename="past_timeoff_requests")
router.register(r"manager-timeoff-approval", ManagerTimeoffApprovalViewSet, basename="manager_timeoff_approval")
router.register(r"timeoff-balance", TimeoffBalanceViewSet, basename="timeoff_balance")
router.register(r"decisioned-timeoff", DecisionedTimeOffViewSet, basename="decisioned_timeoff")
router.register(r"calendar-events", CalendarEventViewSet, basename="calendar_events")

clock_router = DefaultRouter()
clock_router.register(r"user-clock-data", UserClockDataAPIView, basename="clock_in_out_get")
clock_router.register(r"clock-in-out", ClockInOutCreate, basename="clock_in_out_post")
clock_router.register(r"on-shift", UserClockOnShiftViewSet, basename="on_shift")


urlpatterns = [
    # Auth Custom Admin Site URLS
    path('', RedirectView.as_view(url='/auth/login', permanent=False)),
    path("auth/", include("hrmsauth.url")),
    path("auth/ptobalance/", include("ptobalance.url")),
    path("auth/timeoffreq/", include("timeoffreq.urls")),
    path("auth/clock/", include("timeclock.url")),
    path("auth/punchreport/", include("punchreport.url")),
    path("auth/onshift/", include("onshift.url")),
    path("auth/timeoff/", include("timeoff_management.url")),
    path("auth/department/", include("deptleaves.url")),
    path("auth/time-off-balance/", include("usertimeoffbalance.url")),
    path("auth/decisioned-timeoff/", include("decisionedtimeoff.urls")),
    path("auth/user-management/", include("usermanagement.urls")),
    path("api/leave-type-dropdown/", DepartmentLeaveTypeDropdownView.as_view(), name="leave-type-dropdown"),
    path("api/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path('auth/shiftmanagement/', include('shiftmanagement.urls')),
    path("api/", include(router.urls)),
    path("api/clock/", include(clock_router.urls)),  # API for clock functionality
    # Admin URLs
    path("admin/", hrms_admin_site.urls),
    # Yaml schema generation # Api Documentation Related URLS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # It's also good practice to serve static files this way in development,
    # though collectstatic is used in production.
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Optional, but good for dev
