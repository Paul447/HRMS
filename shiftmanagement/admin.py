# shiftmanagement/admin.py

from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta, time, date
import pytz
from django.conf import settings

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
    """Settings for SquadShift admin interface."""
    list_display = ('id', 'squad', 'shift_type', 'shift_start', 'shift_end')
    list_filter = ('squad', 'shift_type')
    search_fields = ('squad__name', 'shift_type__name')
    ordering = ('shift_start', 'squad__name')
    change_list_template = 'admin/shiftmanagement/squadshift/change_list.html'

from datetime import datetime, time, timedelta
import pytz
from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from .models import Squad, SquadShift, ShiftType

class ShiftGenerationConfig:
    """Configuration for shift generation."""
    REFERENCE_DATE = datetime(2024, 7, 1, 6, 0, 0, tzinfo=pytz.UTC)
    LOCAL_TIMEZONE = pytz.timezone('America/Chicago')
    TARGET_DAYS = 14
    MAX_SLOTS = (TARGET_DAYS + 60) * 2
    DEBUG_ENABLED = True

    def __init__(self, base_pattern=None):
        """Initialize with customizable base pattern."""
        self.BASE_PATTERN = base_pattern or [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0]
        self.validate()

    def validate(self):
        """Validate configuration settings."""
        if not self.BASE_PATTERN:
            raise ValueError("BASE_PATTERN must not be empty.")
        if self.TARGET_DAYS <= 0:
            raise ValueError("TARGET_DAYS must be positive.")
        if self.MAX_SLOTS <= 0:
            raise ValueError("MAX_SLOTS must be positive.")

class ShiftPattern:
    """Handles shift pattern logic."""
    def __init__(self, config):
        self.config = config

    def is_squad_on(self, squad_code, day_index):
        """Determine if a squad is working based on the pattern."""
        is_on = self.config.BASE_PATTERN[day_index] if squad_code in ['A', 'C'] else \
                (1 - self.config.BASE_PATTERN[day_index])
        return bool(is_on)

    def get_shift_type(self, squad_code, day_index, is_first_half, day_shift, night_shift):
        """Determine shift type for a squad."""
        if squad_code in ['A', 'B']:
            return day_shift if is_first_half else night_shift
        return night_shift if is_first_half else day_shift

class ShiftGenerationUtils:
    """Helper methods for shift generation."""
    def __init__(self, config):
        self.config = config

    def log_debug(self, message):
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] {message}")

    def get_next_shift_start(self):
        """Calculate next shift start time (6 AM or 6 PM) in UTC."""
        last_shift = SquadShift.objects.order_by('-shift_end').first()
        local_tz = self.config.LOCAL_TIMEZONE

        if last_shift:
            last_end_local = last_shift.shift_end.astimezone(local_tz)
            last_end_date = last_end_local.date()
            if last_end_local.hour == 6:  # Night shift ended at 6 AM
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(6, 0)))
            elif last_end_local.hour == 18:  # Day shift ended at 6 PM
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(18, 0)))
            else:
                next_start_local = local_tz.localize(
                    datetime.combine(last_end_date + timedelta(days=1), time(6, 0))
                )
        else:
            current_year = datetime.now(tz=pytz.UTC).year
            next_start_local = local_tz.localize(datetime(current_year, 6, 29, 6, 0))

        self.log_debug(f"Next shift starts: {next_start_local} (Local)")
        return next_start_local.astimezone(pytz.UTC)

    def get_existing_shifts(self):
        """Retrieve existing shifts to avoid duplicates."""
        shifts = SquadShift.objects.filter(
            shift_start__gte=self.config.REFERENCE_DATE
        ).values_list('squad__id', 'shift_start', 'shift_type__name')
        shift_set = {(squad_id, start.replace(microsecond=0), shift_type_name)
                     for squad_id, start, shift_type_name in shifts}
        self.log_debug(f"Fetched {len(shift_set)} existing shifts.")
        return shift_set

    def ensure_shift_types(self):
        """Ensure DAY and NIGHT shift types exist."""
        day_shift, day_created = ShiftType.objects.get_or_create(name='DAY')
        night_shift, night_created = ShiftType.objects.get_or_create(name='NIGHT')
        if day_created:
            self.log_debug("Created ShiftType: DAY")
        if night_created:
            self.log_debug("Created ShiftType: NIGHT")
        return day_shift, night_shift

class ShiftGenerator:
    """Logic for generating squad shifts."""
    def __init__(self, config, utils, pattern):
        self.config = config
        self.utils = utils
        self.pattern = pattern

    def generate_shifts(self):
        """Generate shifts for the target period."""
        self.utils.log_debug("Starting shift generation.")
        day_shift, night_shift = self.utils.ensure_shift_types()
        new_shifts = []
        generated_count = 0
        start_dt_utc = self.utils.get_next_shift_start()
        start_dt_local = start_dt_utc.astimezone(self.config.LOCAL_TIMEZONE)
        current_date = start_dt_local.date()
        existing_shifts = self.utils.get_existing_shifts()
        squads = list(Squad.objects.all())

        if not squads:
            self.utils.log_debug("No squads found. Aborting.")
            return 0

        self.utils.log_debug(f"Found {len(squads)} squads.")
        end_date = current_date + timedelta(days=self.config.TARGET_DAYS)
        self.utils.log_debug(f"Target end date: {end_date}")

        iteration_count = 0
        while current_date < end_date and iteration_count < self.config.MAX_SLOTS:
            for hour in [6, 18]:  # 6 AM (DAY), 6 PM (NIGHT)
                iteration_count += 1
                slot_start_local = self.config.LOCAL_TIMEZONE.localize(
                    datetime.combine(current_date, time(hour, 0))
                )
                slot_end_local = slot_start_local + timedelta(hours=12) if hour == 6 else \
                    self.config.LOCAL_TIMEZONE.localize(
                        datetime.combine(current_date + timedelta(days=1), time(6, 0))
                    )
                slot_start_utc = slot_start_local.astimezone(pytz.UTC)
                slot_end_utc = slot_end_local.astimezone(pytz.UTC)
                slot_type = 'DAY' if hour == 6 else 'NIGHT'

                self.utils.log_debug(f"Processing slot: {slot_start_local.strftime('%Y-%m-%d %H:%M %Z%z')} ({slot_type})")

                days_since_ref = (current_date - self.config.REFERENCE_DATE.date()).days
                day_index = days_since_ref % len(self.config.BASE_PATTERN)
                is_first_half = (days_since_ref % 28) < 14

                for squad in squads:
                    is_on = self.pattern.is_squad_on(squad.name, day_index)
                    if not is_on:
                        self.utils.log_debug(f"Squad {squad.name}: OFF on day index {day_index}.")
                        continue

                    shift_type = self.pattern.get_shift_type(
                        squad.name, day_index, is_first_half, day_shift, night_shift
                    )
                    if shift_type.name != slot_type:
                        self.utils.log_debug(f"Squad {squad.name}: Assigned {shift_type.name}, slot is {slot_type}. Skipping.")
                        continue

                    shift_id = (squad.id, slot_start_utc.replace(microsecond=0), shift_type.name)
                    if shift_id not in existing_shifts:
                        new_shifts.append(SquadShift(
                            squad=squad,
                            shift_type=shift_type,
                            shift_start=slot_start_utc,
                            shift_end=slot_end_utc
                        ))
                        generated_count += 1
                        existing_shifts.add(shift_id)
                        self.utils.log_debug(f"Added shift: {slot_start_local} to {slot_end_local}")

            current_date += timedelta(days=1)

        if new_shifts:
            self.utils.log_debug(f"Creating {len(new_shifts)} new shifts.")
            SquadShift.objects.bulk_create(new_shifts, ignore_conflicts=True)
            self.utils.log_debug("Bulk creation completed.")
        else:
            self.utils.log_debug("No new shifts to create.")

        self.utils.log_debug(f"Generation complete. Total generated: {generated_count}")
        return generated_count

class SquadShiftAdminConfig:
    """Configuration for SquadShift admin interface."""
    list_display = ('squad', 'shift_type', 'shift_start', 'shift_end')
    list_filter = ('squad', 'shift_type')
    search_fields = ('squad__name', 'shift_type__name')
    ordering = ('-shift_start',)
    change_list_template = 'admin/shiftmanagement/squadshift/change_list.html'

@admin.register(SquadShift)
class SquadShiftAdmin(admin.ModelAdmin):
    """Admin interface for managing squad shifts."""
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        config = ShiftGenerationConfig()
        self.utils = ShiftGenerationUtils(config)
        self.pattern = ShiftPattern(config)
        self.generator = ShiftGenerator(config, self.utils, self.pattern)
        admin_config = SquadShiftAdminConfig()
        self.list_display = admin_config.list_display
        self.list_filter = admin_config.list_filter
        self.search_fields = admin_config.search_fields
        self.ordering = admin_config.ordering
        self.change_list_template = admin_config.change_list_template

    def get_urls(self):
        """Add custom URL for shift generation."""
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
        """Handle shift generation via admin interface."""
        if request.method == 'POST':
            count = self.generator.generate_shifts()
            if count > 0:
                messages.success(request, f"Generated {count} new squad shifts.")
            else:
                messages.info(request, "No new shifts generated. Schedule may be up to date or no squads found.")
            return redirect('admin:shiftmanagement_squadshift_changelist')

        messages.error(request, "Shift generation requires a POST request.")
        return redirect('admin:shiftmanagement_squadshift_changelist')