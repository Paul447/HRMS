"""
URL configuration for the HRMS project.

This file defines the URL patterns for the Django project, including:
- API endpoints under /api/v1/ (versioned API with DRF routers)
- App-specific routes under /auth/ (e.g., authentication, time-off requests, punch reports)
- Custom admin site at /admin/
- Static and media file serving for development
- Root redirect to login page
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Custom Admin Site
from adminorganizer.admin.admin_site import hrms_admin_site

# ViewSets
from hrmsauth.views import UserInfoViewSet
from punchreport.views import PunchReportViewSet
from payperiod.views import (
    PayPeriodUptoTodayViewSet,
    PayPeriodViewSetForPastTimeOffRequest,
    PayPeriodViewSetForCurrentFutureTimeOffRequest,
)
from timeclock.views import UserClockDataAPIView, ClockInOutCreate
from ptobalance.views import PTOBalanceViewSet
from deptleaves.views import DepartmentLeavesViewSet
from onshift.views import UserClockOnShiftViewSet
from notificationapp.views import NotificationViewSet
from timeoffreq.views import (
    TimeoffRequestViewSetEmployee,
    PastTimeOffRequestViewSet,
    DepartmentLeaveTypeDropdownView,
)
from timeoff_management.views import ManagerTimeoffApprovalViewSet
from usertimeoffbalance.views import TimeoffBalanceViewSet
from decisionedtimeoff.views import DecisionedTimeOffViewSet
from usermanagement.views import ChangePasswordView
from shiftmanagement.views import CalendarEventViewSet

# ==========================
# MAIN API ROUTER (v1)
# ==========================timeoffrequests/

api_v1_router = DefaultRouter()

# --- User & Profile ---
api_v1_router.register(r"user-info", UserInfoViewSet, basename="user_info")

# --- Punch & Pay Period ---
api_v1_router.register(r"punch-report", PunchReportViewSet, basename="punch_report")
api_v1_router.register(r"pay-period", PayPeriodUptoTodayViewSet, basename="pay_period_upto_today")
api_v1_router.register(r"past-pay-period", PayPeriodViewSetForPastTimeOffRequest, basename="past_pay_period")
api_v1_router.register(r"future-pay-period", PayPeriodViewSetForCurrentFutureTimeOffRequest, basename="future_pay_period")
api_v1_router.register(r"current-future-pay-period", PayPeriodViewSetForCurrentFutureTimeOffRequest, basename="current_future_pay_period")

# --- PTO & Leave Balance ---
api_v1_router.register(r"pto-balance", PTOBalanceViewSet, basename="pto_balance")
api_v1_router.register(r"department-leaves", DepartmentLeavesViewSet, basename="department_leaves")
api_v1_router.register(r"timeoff-balance", TimeoffBalanceViewSet, basename="timeoff_balance")

# --- Time Off Management ---
api_v1_router.register(r"timeoffrequests", TimeoffRequestViewSetEmployee, basename="timeoff_requests")
api_v1_router.register(r"past-timeoff-requests", PastTimeOffRequestViewSet, basename="past_timeoff_requests")
api_v1_router.register(r"manager-timeoff-approval", ManagerTimeoffApprovalViewSet, basename="manager_timeoff_approval")
api_v1_router.register(r"decisioned-timeoff", DecisionedTimeOffViewSet, basename="decisioned_timeoff")
api_v1_router.register(r"calendar-events", CalendarEventViewSet, basename="calendar_events")

# --- Notification ---
api_v1_router.register(r"notifications", NotificationViewSet, basename="notifications")

# --- Clock-Specific ---
clock_router = DefaultRouter()
clock_router.register(r"user-clock-data", UserClockDataAPIView, basename="user_clock_data")
clock_router.register(r"clock-in-out", ClockInOutCreate, basename="clock_in_out")
clock_router.register(r"on-shift", UserClockOnShiftViewSet, basename="on_shift")

# ==========================
# API v1 ROUTES
# ==========================

api_v1_patterns = [
    path("", include(api_v1_router.urls)),
    path("clock/", include(clock_router.urls)),
    path("leave-type-dropdown/", DepartmentLeaveTypeDropdownView.as_view(), name="leave-type-dropdown"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# ==========================
# MAIN URLPATTERNS
# ==========================

urlpatterns = [
    # Redirect root to login page for unauthenticated users
    path("", RedirectView.as_view(url="/auth/login/", permanent=False)),
    # Admin site
    path("admin/", hrms_admin_site.urls),
    # App module URLs (all require authentication unless specified in app URLs)
    path("auth/", include("hrmsauth.url", namespace="hrmsauth")),
    path("auth/pto-balance/", include("ptobalance.url", namespace="ptobalance")),
    path("auth/timeoff-request/", include("timeoffreq.urls", namespace="timeoffreq")),
    path("auth/clock/", include("timeclock.url", namespace="timeclock")),
    path("auth/punch-report/", include("punchreport.url", namespace="punchreport")),
    path("auth/on-shift/", include("onshift.url", namespace="onshift")),
    path("auth/timeoff-management/", include("timeoff_management.url", namespace="timeoff_management")),
    path("auth/department/", include("deptleaves.url", namespace="deptleaves")),
    path("auth/timeoff-balance/", include("usertimeoffbalance.url", namespace="usertimeoffbalance")),
    path("auth/decisioned-timeoff/", include("decisionedtimeoff.urls", namespace="decisionedtimeoff")),
    path("auth/user-management/", include("usermanagement.urls", namespace="usermanagement")),
    path("auth/shift-management/", include("shiftmanagement.urls", namespace="shiftmanagement")),
    # Versioned API (v1)
    path("api/v1/", include((api_v1_patterns, "v1"), namespace="v1")),
]

# Serve media files during development only; in production, configure web server (e.g., Nginx) to serve media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)