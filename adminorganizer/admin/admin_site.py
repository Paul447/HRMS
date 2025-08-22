from django.contrib import admin
from django.urls import reverse as urls_reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import  GroupAdmin

# Time Clock Management
from timeclock.admin import ClockAdmin
from timeclock.models import Clock

# Balance and Requests Management
from ptobalance.admin import PTOBalanceAdmin
from ptobalance.models import PTOBalance
from timeoffreq.admin import TimeoffreqAdmin
from timeoffreq.models import TimeoffRequest

# User Management
from yearofexperience.admin import YearOfExperienceAdmin
from yearofexperience.models import YearOfExperience
from department.admin import DepartmentAdmin, UserProfileAdmin, CustomUserAdmin
from department.models import Department, UserProfile
from notificationapp.models import Notification
from notificationapp.admin import NotificationAdmin

# Balance and Determining Factors
from employeetype.admin import EmployeeTypeAdmin
from payfrequency.admin import PayFrequencyAdmin
from accuralrates.admin import AccrualRatesAdmin
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from accuralrates.models import AccrualRates

# Adjustments
from holiday.admin import HolidayAdmin
from holiday.models import Holiday
from payperiod.admin import PayPeriodAdmin
from payperiod.models import PayPeriod
from allowipaddress.admin import AllowIpAddressAdmin
from allowipaddress.models import AllowIpAddress
from sickpolicy.admin import SickLeaveProratedValueAdmin, MaxSickValueAdmin
from sickpolicy.models import SickLeaveProratedValue, MaxSickValue
from unverifiedsickleave.admin import SickLeaveBalanceAdmin
from unverifiedsickleave.models import SickLeaveBalance

# Leave Type Assignment
from leavetype.admin import LeaveTypeAdmin, DepartmentBasedLeaveTypeAdmin
from leavetype.models import LeaveType, DepartmentBasedLeaveType
from shiftmanagement.admin import SquadAdmin , ShiftTypeAdmin, EmployeeAdmin, SquadShiftAdmin
from shiftmanagement.models import Squad, ShiftType, Employee, SquadShift

# Celery (Beat + Results) Models
from django_celery_beat.models import (
    PeriodicTask, CrontabSchedule, IntervalSchedule,
    SolarSchedule, ClockedSchedule
)
from django_celery_results.models import TaskResult, GroupResult


class CustomAdminSite(admin.AdminSite):
    site_header = "University Police Department Admin"
    site_title = "University Police HRMS | Admin Portal"
    index_title = "Welcome to University Police HRMS Admin"

    def get_app_list(self, request):
        app_list = []

        def create_model_entry(model_class, name, app_label):
            return {
                "model": model_class,
                "name": name,
                "admin_url": urls_reverse(f"admin:{app_label}_{model_class._meta.model_name}_changelist", current_app=self.name),
                "add_url": urls_reverse(f"admin:{app_label}_{model_class._meta.model_name}_add", current_app=self.name),
                "object_name": model_class._meta.model_name,
                "perms": {
                    "add": request.user.has_perm(f"{app_label}.add_{model_class._meta.model_name}"),
                    "change": request.user.has_perm(f"{app_label}.change_{model_class._meta.model_name}"),
                    "delete": request.user.has_perm(f"{app_label}.delete_{model_class._meta.model_name}"),
                    "view": request.user.has_perm(f"{app_label}.view_{model_class._meta.model_name}")
                }
            }

        # 1. User & Organization
        user_org_models = [
            create_model_entry(User, "Users", "auth"),
            create_model_entry(Group, "Groups", "auth"),
            create_model_entry(YearOfExperience, "Years of Experience", "yearofexperience"),
            create_model_entry(UserProfile, "Employee Profiles", "department"),
            create_model_entry(Department, "Department Units", "department")
        ]
        app_list.append({"name": "User & Organization", "app_label": "user_organization", "has_module_perms": True, "models": user_org_models})

        # 2. Time Tracking
        time_tracking_models = [
            create_model_entry(Clock, "Clock In/Out", "timeclock")
        ]
        app_list.append({"name": "Time Tracking", "app_label": "time_tracking", "has_module_perms": True, "models": time_tracking_models})

        # 3. Leave & Balance
        user_balance = [
            create_model_entry(PTOBalance, "PTO Balances", "ptobalance"),
            create_model_entry(SickLeaveBalance, "Sick Leave Balances", "unverifiedsickleave")

        ]

        app_list.append({"name": "User Balance", "app_label": "leave_balance_management", "has_module_perms": True, "models": user_balance})

        # Leave Management
        leave_management_models = [
            create_model_entry(TimeoffRequest, "Time Off Requests", "timeoffreq"),
            create_model_entry(LeaveType, "Leave Types", "leavetype"),
            create_model_entry(DepartmentBasedLeaveType, "Unit Based Leave Types", "leavetype"),
            create_model_entry(EmployeeType, "Employee Types", "employeetype"),
            create_model_entry(Pay_Frequency, "Pay Frequencies", "payfrequency"),
        ]
        app_list.append({"name": "Leave Management", "app_label": "leave_management", "has_module_perms": True, "models": leave_management_models})
        # 4. Shift Management and Assignments
        shift_management_models = [
            create_model_entry(Squad, "Squads", "shiftmanagement"),
            create_model_entry(ShiftType, "Shift Types", "shiftmanagement"),
            create_model_entry(Employee, "Employees", "shiftmanagement"),
            create_model_entry(SquadShift, "Squad Shifts", "shiftmanagement")
        ]
        app_list.append({"name": "Shift Management", "app_label": "shift_management", "has_module_perms": True, "models": shift_management_models})

        # 5. Compensation & Accruals
        comp_accruals_models = [
            create_model_entry(AccrualRates, "Accrual Rates", "accuralrates"),
            create_model_entry(SickLeaveProratedValue, "Sick Leave Prorated Value", "sickpolicy"),
            create_model_entry(MaxSickValue, "Maximum Sick Values", "sickpolicy"),
        ]
        app_list.append({"name": "Compensation & Accruals", "app_label": "compensation_accruals", "has_module_perms": True, "models": comp_accruals_models})

        # 6. System Adjustments
        system_adjustments_models = [
            create_model_entry(Holiday, "Holidays", "holiday"),
            create_model_entry(PayPeriod, "Pay Periods", "payperiod"),
            create_model_entry(AllowIpAddress, "Whitelisted IP Addresses", "allowipaddress"),
            create_model_entry(Notification, "Notifications", "notificationapp"),            
        ]
        app_list.append({"name": "System Adjustments", "app_label": "system_adjustments", "has_module_perms": True, "models": system_adjustments_models})

        # 7. Background Tasks (Celery)
        celery_models = [
            create_model_entry(PeriodicTask, "Periodic Tasks", "django_celery_beat"),
            create_model_entry(CrontabSchedule, "Crontab Schedules", "django_celery_beat"),
            create_model_entry(IntervalSchedule, "Interval Schedules", "django_celery_beat"),
            create_model_entry(SolarSchedule, "Solar Schedules", "django_celery_beat"),
            create_model_entry(ClockedSchedule, "Clocked Schedules", "django_celery_beat"),
            create_model_entry(TaskResult, "Task Results", "django_celery_results"),
            create_model_entry(GroupResult, "Group Results", "django_celery_results"),
        ]
        app_list.append({"name": "Background Tasks (Celery)", "app_label": "celery_management", "has_module_perms": True, "models": celery_models})

        return app_list


# Instantiate custom admin site
hrms_admin_site = CustomAdminSite(name="hrms_admin")

# Register models
hrms_admin_site.register(Clock, ClockAdmin)
hrms_admin_site.register(PTOBalance, PTOBalanceAdmin)
hrms_admin_site.register(YearOfExperience, YearOfExperienceAdmin)
hrms_admin_site.register(Department, DepartmentAdmin)
hrms_admin_site.register(UserProfile, UserProfileAdmin)
hrms_admin_site.register(User, CustomUserAdmin)
hrms_admin_site.register(Group, GroupAdmin)
hrms_admin_site.register(EmployeeType, EmployeeTypeAdmin)
hrms_admin_site.register(Pay_Frequency, PayFrequencyAdmin)
hrms_admin_site.register(AccrualRates, AccrualRatesAdmin)
hrms_admin_site.register(Holiday, HolidayAdmin)
hrms_admin_site.register(PayPeriod, PayPeriodAdmin)
hrms_admin_site.register(LeaveType, LeaveTypeAdmin)
hrms_admin_site.register(DepartmentBasedLeaveType, DepartmentBasedLeaveTypeAdmin)
hrms_admin_site.register(AllowIpAddress, AllowIpAddressAdmin)
hrms_admin_site.register(Notification, NotificationAdmin)
hrms_admin_site.register(SickLeaveProratedValue, SickLeaveProratedValueAdmin)
hrms_admin_site.register(MaxSickValue, MaxSickValueAdmin)
hrms_admin_site.register(SickLeaveBalance, SickLeaveBalanceAdmin)
hrms_admin_site.register(TimeoffRequest, TimeoffreqAdmin)

# Register Shift Management models
hrms_admin_site.register(Squad, SquadAdmin)
hrms_admin_site.register(ShiftType, ShiftTypeAdmin)
hrms_admin_site.register(Employee, EmployeeAdmin)
hrms_admin_site.register(SquadShift, SquadShiftAdmin)

# Register Celery models
hrms_admin_site.register(PeriodicTask)
hrms_admin_site.register(CrontabSchedule)
hrms_admin_site.register(IntervalSchedule)
hrms_admin_site.register(SolarSchedule)
hrms_admin_site.register(ClockedSchedule)
hrms_admin_site.register(TaskResult)
hrms_admin_site.register(GroupResult)
