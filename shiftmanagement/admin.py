# shiftmanagement/admin.py

from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from .config import ShiftGenerationConfig
from .pattern_manager import ShiftPatternManager
from .query_helper import ShiftQueryHelper
from .time_calculator import ShiftTimeCalculator
from .generator_core import ShiftGeneratorCore
from .models import SquadShift

# Import your models (SquadShift replaces ShiftAssignment)
from .models import Squad, ShiftType, Employee, SquadShift


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'squad')
    list_filter = ('squad',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class SquadShiftAdminConfig:
    """Settings for the admin interface."""
    list_display = ('squad', 'shift_type', 'shift_start', 'shift_end')
    list_filter = ('squad', 'shift_type')
    search_fields = ('squad__name', 'shift_type__name')
    ordering = ('-shift_start',)
    change_list_template = 'admin/shiftmanagement/squadshift/change_list.html'

@admin.register(SquadShift)
class SquadShiftAdmin(admin.ModelAdmin):
    """Admin panel for managing squad shifts."""
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.config = ShiftGenerationConfig()
        self.pattern_manager = ShiftPatternManager(self.config)
        self.query_helper = ShiftQueryHelper(self.config)
        self.time_calculator = ShiftTimeCalculator(self.config)
        self.generator_core = ShiftGeneratorCore(
            self.config,
            self.pattern_manager,
            self.query_helper,
            self.time_calculator
        )
        admin_config = SquadShiftAdminConfig()
        self.list_display = admin_config.list_display
        self.list_filter = admin_config.list_filter
        self.search_fields = admin_config.search_fields
        self.ordering = admin_config.ordering
        self.change_list_template = admin_config.change_list_template

    def get_urls(self):
        """Add a URL for generating shifts."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-shifts/',
                self.admin_site.admin_view(self.generate_shifts_view),
                name='shiftmanagement_squadshift_generate_shifts'
            ),
        ]
        return custom_urls + urls

    def generate_shifts_view(self, request):
        """Handle shift generation via the admin panel."""
        if request.method == 'POST':
            try:
                count = self.generator_core.generate_shifts()
                if count > 0:
                    messages.success(request, f"Generated {count} new squad shifts.")
                else:
                    messages.info(request, "No new shifts generated. Schedule may be up to date or no squads found.")
            except Exception as e:
                messages.error(request, f"Error during shift generation: {e}")
                if self.config.DEBUG_ENABLED:
                    print(f"ERROR: {e}")
            return redirect('admin:shiftmanagement_squadshift_changelist')
        messages.error(request, "Shift generation requires a POST request.")
        return redirect('admin:shiftmanagement_squadshift_changelist')