from django.contrib import admin
from django.urls import reverse as urls_reverse # Import Django's reverse function
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Time Clock Management
# -------------------------------------------------------
from timeclock.admin import ClockAdmin
from timeclock.models import Clock
# ---------------------------------------------------------

# Balance and Requests Management
# -------------------------------------------------------
from ptobalance.admin import PTOBalanceAdmin
from ptorequest.admin import PTORequestsAdmin
from ptobalance.models import PTOBalance
from ptorequest.models import PTORequests
from timeoffreq.admin import TimeoffreqAdmin
from timeoffreq.models import TimeoffRequest
# -------------------------------------------------------

# User Management
# -------------------------------------------------------
from yearofexperience.admin import YearOfExperienceAdmin
from department.admin import DepartmentAdmin, UserProfileAdmin,CustomUserAdmin
from yearofexperience.models import YearOfExperience
from department.models import Department, UserProfile
from notificationapp.models import Notification
from notificationapp.admin import NotificationAdmin
# -------------------------------------------------------

# Balance and Determining Factors
# -------------------------------------------------------
from employeetype.admin import EmployeeTypeAdmin
from payfrequency.admin import PayFrequencyAdmin
from accuralrates.admin import AccrualRatesAdmin
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from accuralrates.models import AccrualRates
# -------------------------------------------------------

# Adjustments needing things
# -------------------------------------------------------
from biweeklycron.admin import BiweeklyCronAdmin
from holiday.admin import HolidayAdmin
from payperiod.admin import PayPeriodAdmin
from biweeklycron.models import BiweeklyCron
from holiday.models import Holiday
from payperiod.models import PayPeriod
from allowipaddress.admin import AllowIpAddressAdmin
from allowipaddress.models import AllowIpAddress
from sickpolicy.admin import SickLeaveProratedValueAdmin, MaxSickValueAdmin
from sickpolicy.models import SickLeaveProratedValue ,MaxSickValue
from unverifiedsickleave.admin import SickLeaveBalanceAdmin
from unverifiedsickleave.models import SickLeaveBalance
# -------------------------------------------------------

# Leave Type and Department Based Leave Type Assignment
# -------------------------------------------------------
from leavetype.admin import LeaveTypeAdmin, DepartmentBasedLeaveTypeAdmin
from leavetype.models import LeaveType, DepartmentBasedLeaveType
# -------------------------------------------------------

class CustomAdminSite(admin.AdminSite):
    """
    Custom Django Admin site with enhanced configuration for better organization
    and usability of the admin interface.
    """
    site_header = 'HRMS Admin'
    site_title = 'DPS HRMS | Admin Portal'
    index_title = 'Welcome to DPS HRMS Admin'

    def get_app_list(self, request):
        app_list = []

        # Helper function to create model dictionaries
        def create_model_entry(model_class, name, app_label):
            return {
                'model': model_class,
                'name': name,
                'admin_url': urls_reverse(f'admin:{app_label}_{model_class._meta.model_name}_changelist', current_app=self.name),
                'add_url': urls_reverse(f'admin:{app_label}_{model_class._meta.model_name}_add', current_app=self.name),
                'object_name': model_class._meta.model_name,
                'perms': {
                    'add': request.user.has_perm(f'{app_label}.add_{model_class._meta.model_name}'),
                    'change': request.user.has_perm(f'{app_label}.change_{model_class._meta.model_name}'),
                    'delete': request.user.has_perm(f'{app_label}.delete_{model_class._meta.model_name}'),
                    'view': request.user.has_perm(f'{app_label}.view_{model_class._meta.model_name}'),
                },
            }

        # 1. User & Organizational Management
        user_org_models = [
            create_model_entry(User, 'Users', 'auth'),
            create_model_entry(Group, 'Groups', 'auth'),
            create_model_entry(YearOfExperience, 'Years of Experience', 'yearofexperience'),
            create_model_entry(UserProfile, 'User Profiles', 'department'),
            create_model_entry(Department, 'Departments', 'department'),
        ]
        app_list.append({
            'name': 'User & Organization',
            'app_label': 'user_organization', # Unique label for this group
            'has_module_perms': True,
            'models': user_org_models,
        })

        # 2. Time Tracking
        time_tracking_models = [
            create_model_entry(Clock, 'Clocks', 'timeclock'),
        ]
        app_list.append({
            'name': 'Time Tracking',
            'app_label': 'time_tracking',
            'has_module_perms': True,
            'models': time_tracking_models,
        })

        # 3. Leave & Balance Management
        leave_balance_models = [
            create_model_entry(PTOBalance, 'PTO Balances', 'ptobalance'),
            create_model_entry(PTORequests, 'Time Off Requests', 'ptorequest'),
            create_model_entry(TimeoffRequest, 'Time Off Requests', 'timeoffreq'),
            create_model_entry(LeaveType, 'Leave Types', 'leavetype'),
            create_model_entry(DepartmentBasedLeaveType, 'Department Based Leave Types', 'leavetype'),
        ]
        app_list.append({
            'name': 'Leave & Balance',
            'app_label': 'leave_balance_management',
            'has_module_perms': True,
            'models': leave_balance_models,
        })

        # 4. Compensation & Accruals
        comp_accruals_models = [
            create_model_entry(EmployeeType, 'Employee Types', 'employeetype'),
            create_model_entry(Pay_Frequency, 'Pay Frequencies', 'payfrequency'),
            create_model_entry(AccrualRates, 'Accrual Rates', 'accuralrates'),
        ]
        app_list.append({
            'name': 'Compensation & Accruals',
            'app_label': 'compensation_accruals',
            'has_module_perms': True,
            'models': comp_accruals_models,
        })

        # 5. System Adjustments & Holidays
        system_adjustments_models = [
            create_model_entry(BiweeklyCron, 'Biweekly Cron Jobs', 'biweeklycron'),
            create_model_entry(Holiday, 'Holidays', 'holiday'),
            create_model_entry(PayPeriod, 'Pay Periods', 'payperiod'),
            create_model_entry(AllowIpAddress, 'Allowed IP Addresses', 'allowipaddress'),
            create_model_entry(Notification, 'Notifications', 'notificationapp'),
            create_model_entry(SickLeaveProratedValue, 'Sick Leave Prorated Value', 'sickpolicy'),
            create_model_entry(MaxSickValue, 'Maximum Sick Values', 'sickpolicy'),
            create_model_entry(SickLeaveBalance, 'Sick Leave Balances', 'unverifiedsickleave'),
        ]
        app_list.append({
            'name': 'System Adjustments',
            'app_label': 'system_adjustments',
            'has_module_perms': True,
            'models': system_adjustments_models,
        })

        return app_list

# Instantiate your custom admin site
hrms_admin_site = CustomAdminSite(name='hrms_admin')

# Register your models with the custom admin site instance
# Ensure these are NOT registered with the default admin.site elsewhere if you want them exclusively here.
hrms_admin_site.register(Clock, ClockAdmin)
hrms_admin_site.register(PTOBalance, PTOBalanceAdmin)
hrms_admin_site.register(PTORequests, PTORequestsAdmin)
hrms_admin_site.register(YearOfExperience, YearOfExperienceAdmin)
hrms_admin_site.register(Department, DepartmentAdmin)
hrms_admin_site.register(UserProfile, UserProfileAdmin)
hrms_admin_site.register(User, CustomUserAdmin)
hrms_admin_site.register(Group, GroupAdmin)
hrms_admin_site.register(EmployeeType, EmployeeTypeAdmin)
hrms_admin_site.register(Pay_Frequency, PayFrequencyAdmin)
hrms_admin_site.register(AccrualRates, AccrualRatesAdmin)
hrms_admin_site.register(BiweeklyCron, BiweeklyCronAdmin)
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
