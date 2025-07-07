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
from .models import Squad, SquadShift, ShiftType # Assuming these are defined in your models.py

# --- 1. Configuration Class ---
class ShiftGenerationConfig:
    """Configuration for shift generation."""
    REFERENCE_DATE = datetime(2025, 7, 14, 6, 0, 0, tzinfo=pytz.UTC)
    LOCAL_TIMEZONE = pytz.timezone('America/Chicago')
    TARGET_DAYS = 14
    MAX_SLOTS = (TARGET_DAYS + 60) * 2 # Safety limit to prevent infinite loops
    DEBUG_ENABLED = True

    def __init__(self, base_pattern=None):
        """Initialize with customizable base pattern."""
        # BASE_PATTERN: 1 indicates working day for A/C, 0 for B/D
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

# --- 2. Shift Pattern Management ---
class ShiftPatternManager:
    """
    Manages the logic for determining if a squad is working and their shift type
    based on predefined patterns.
    """
    def __init__(self, config: ShiftGenerationConfig):
        self.config = config

    def is_squad_working_day(self, squad_code: str, day_index: int) -> bool:
        """
        Determines if a squad is scheduled to work on a given day based on the BASE_PATTERN.
        Squads A and C follow the pattern directly (1 = working, 0 = off).
        Squads B and D work when A and C are off (inverted pattern).
        """
        pattern_value = self.config.BASE_PATTERN[day_index % len(self.config.BASE_PATTERN)]
        if squad_code in ['A', 'C']:
            return bool(pattern_value)
        elif squad_code in ['B', 'D']:
            return not bool(pattern_value)
        return False # Should not happen with expected squad codes

    def get_squad_shift_type_for_day(self, squad_code: str, days_since_ref: int,
                                     day_shift_type: ShiftType, night_shift_type: ShiftType) -> ShiftType:
        """
        Determines the specific shift type (DAY/NIGHT) for a squad on a given day
        within a 28-day consistent cycle.

        - Even 28-day cycles (0, 2, 4...) for squads A & B are DAY shifts.
        - Odd 28-day cycles (1, 3, 5...) for squads A & B are NIGHT shifts.
        - Squads C & D do the opposite of A & B for the current cycle.
        """
        cycle_number = days_since_ref // 28
        is_a_b_day_shift = (cycle_number % 2 == 0) # True if A/B should be on day shift for this cycle

        if squad_code in ['C', 'D']:
            return day_shift_type if is_a_b_day_shift else night_shift_type
        else: # Squad A & B
            return night_shift_type if is_a_b_day_shift else day_shift_type

# --- 3. Database Query Helper ---
class ShiftQueryHelper:
    """Helper methods for interacting with the database regarding shifts and shift types."""
    def __init__(self, config: ShiftGenerationConfig):
        self.config = config

    def log_debug(self, message):
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] ShiftQueryHelper: {message}")

    def get_last_shift_end_time_utc(self) -> datetime | None:
        """Retrieves the shift_end time of the most recent SquadShift in UTC."""
        last_shift = SquadShift.objects.order_by('-shift_end').first()
        if last_shift:
            self.log_debug(f"Last shift end found: {last_shift.shift_end}")
            return last_shift.shift_end.astimezone(pytz.UTC)
        self.log_debug("No last shift found.")
        return None

    def get_existing_shifts_set(self) -> set[tuple]:
        """
        Retrieves existing shifts from the database to prevent duplicates.
        Returns a set of tuples: (squad_id, shift_start_datetime_without_micros, shift_type_name).
        """
        shifts = SquadShift.objects.filter(
            shift_start__gte=self.config.REFERENCE_DATE - timedelta(days=7) # Look back a bit to catch overlaps
        ).values_list('squad__id', 'shift_start', 'shift_type__name')
        
        shift_set = {
            (squad_id, start.replace(microsecond=0, tzinfo=pytz.UTC), shift_type_name)
            for squad_id, start, shift_type_name in shifts
        }
        self.log_debug(f"Fetched {len(shift_set)} existing shifts.")
        return shift_set

    def get_or_create_shift_types(self) -> tuple[ShiftType, ShiftType]:
        """Ensures 'DAY' and 'NIGHT' ShiftType objects exist in the database."""
        day_shift, day_created = ShiftType.objects.get_or_create(name='DAY')
        night_shift, night_created = ShiftType.objects.get_or_create(name='NIGHT')
        if day_created:
            self.log_debug("Created ShiftType: DAY")
        if night_created:
            self.log_debug("Created ShiftType: NIGHT")
        return day_shift, night_shift

    def get_all_squads(self) -> list[Squad]:
        """Retrieves all Squad objects."""
        squads = list(Squad.objects.all())
        self.log_debug(f"Found {len(squads)} squads.")
        return squads

    def bulk_create_shifts(self, new_shifts: list[SquadShift]):
        """Performs a bulk creation of new SquadShift objects, ignoring conflicts."""
        if new_shifts:
            self.log_debug(f"Attempting to bulk create {len(new_shifts)} new shifts.")
            SquadShift.objects.bulk_create(new_shifts, ignore_conflicts=True)
            self.log_debug("Bulk creation completed.")
        else:
            self.log_debug("No new shifts to bulk create.")

# --- 4. Shift Time Calculation Helper ---
class ShiftTimeCalculator:
    """Handles calculations related to shift start/end times and timezones."""
    def __init__(self, config: ShiftGenerationConfig):
        self.config = config

    def log_debug(self, message):
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] ShiftTimeCalculator: {message}")

    def get_initial_generation_start_utc(self, last_shift_end_utc: datetime | None) -> datetime:
        """
        Determines the starting point for shift generation.
        If there are existing shifts, it starts from the end of the last one.
        Otherwise, it starts from a default reference point.
        """
        local_tz = self.config.LOCAL_TIMEZONE
        if last_shift_end_utc:
            last_end_local = last_shift_end_utc.astimezone(local_tz)
            last_end_date = last_end_local.date()

            # Determine next 6 AM or 6 PM based on last shift's end time
            if last_end_local.hour < 6: # Ended before 6 AM (e.g., 2 AM) - next start is 6 AM same day
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(6, 0)))
            elif last_end_local.hour < 18: # Ended before 6 PM (e.g., 10 AM) - next start is 6 PM same day
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(18, 0)))
            else: # Ended after 6 PM (e.g., 10 PM) - next start is 6 AM next day
                next_start_local = local_tz.localize(datetime.combine(last_end_date + timedelta(days=1), time(6, 0)))
        else:
            # If no shifts exist, start from a sensible default (e.g., REFERENCE_DATE or current time)
            # For robustness, we'll start from REFERENCE_DATE if no shifts are found.
            # Convert REFERENCE_DATE to local timezone to find the nearest 6 AM or 6 PM
            ref_date_local = self.config.REFERENCE_DATE.astimezone(local_tz)
            if ref_date_local.hour < 6:
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date(), time(6, 0)))
            elif ref_date_local.hour < 18:
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date(), time(18, 0)))
            else:
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date() + timedelta(days=1), time(6, 0)))

        self.log_debug(f"Calculated initial generation start: {next_start_local} (Local)")
        return next_start_local.astimezone(pytz.UTC)

    def get_slot_times_utc(self, current_date: datetime.date, hour: int) -> tuple[datetime, datetime, str]:
        """
        Calculates the UTC start and end times for a 12-hour shift slot.
        Also returns the string representation of the slot type ('DAY' or 'NIGHT').
        """
        local_tz = self.config.LOCAL_TIMEZONE

        slot_start_local = local_tz.localize(datetime.combine(current_date, time(hour, 0)))
        
        if hour == 6: # Day shift (6 AM to 6 PM)
            slot_end_local = slot_start_local + timedelta(hours=12)
            slot_type_name = 'DAY'
        elif hour == 18: # Night shift (6 PM to 6 AM next day)
            slot_end_local = local_tz.localize(datetime.combine(current_date + timedelta(days=1), time(6, 0)))
            slot_type_name = 'NIGHT'
        else:
            raise ValueError("Shift hour must be 6 or 18.")

        slot_start_utc = slot_start_local.astimezone(pytz.UTC)
        slot_end_utc = slot_end_local.astimezone(pytz.UTC)

        self.log_debug(f"Slot: {slot_start_local.strftime('%Y-%m-%d %H:%M %Z%z')} to {slot_end_local.strftime('%Y-%m-%d %H:%M %Z%z')} ({slot_type_name})")
        return slot_start_utc, slot_end_utc, slot_type_name

# --- 5. Core Shift Generation Logic ---
class ShiftGeneratorCore:
    """Orchestrates the generation of squad shifts."""
    def __init__(self, config: ShiftGenerationConfig,
                 pattern_manager: ShiftPatternManager,
                 query_helper: ShiftQueryHelper,
                 time_calculator: ShiftTimeCalculator):
        self.config = config
        self.pattern_manager = pattern_manager
        self.query_helper = query_helper
        self.time_calculator = time_calculator

    def log_debug(self, message):
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] ShiftGeneratorCore: {message}")

    def generate_shifts(self) -> int:
        """
        Generates shifts for the target period based on configuration and patterns.
        Returns the count of newly generated shifts.
        """
        self.log_debug("Starting shift generation process.")

        day_shift_type, night_shift_type = self.query_helper.get_or_create_shift_types()
        squads = self.query_helper.get_all_squads()
        if not squads:
            self.log_debug("No squads found. Aborting shift generation.")
            return 0

        existing_shifts = self.query_helper.get_existing_shifts_set()
        last_shift_end_utc = self.query_helper.get_last_shift_end_time_utc()
        
        # Determine where to start generating from (current time adjusted or after last shift)
        start_generation_dt_utc = self.time_calculator.get_initial_generation_start_utc(last_shift_end_utc)
        start_date_local = start_generation_dt_utc.astimezone(self.config.LOCAL_TIMEZONE).date()

        end_date = start_date_local + timedelta(days=self.config.TARGET_DAYS)
        self.log_debug(f"Generating shifts from {start_date_local} to {end_date}.")

        new_shifts = []
        generated_count = 0
        iteration_count = 0
        current_date = start_date_local

        while current_date < end_date and iteration_count < self.config.MAX_SLOTS:
            for hour in [6, 18]: # Iterate for 6 AM (DAY) and 6 PM (NIGHT) shifts
                iteration_count += 1
                
                # Get the UTC start/end times and slot type for the current 12-hour window
                slot_start_utc, slot_end_utc, slot_type_name = \
                    self.time_calculator.get_slot_times_utc(current_date, hour)
                
                # Calculate days since reference for pattern and cycle determination
                days_since_ref = (current_date - self.config.REFERENCE_DATE.date()).days
                
                for squad in squads:
                    # Check if the squad is scheduled to work on this day
                    if not self.pattern_manager.is_squad_working_day(squad.name, days_since_ref):
                        self.log_debug(f"Squad {squad.name} is OFF on {current_date.strftime('%Y-%m-%d')}.")
                        continue

                    # Determine the specific shift type (DAY/NIGHT) for this squad and cycle
                    assigned_shift_type = self.pattern_manager.get_squad_shift_type_for_day(
                        squad.name, days_since_ref, day_shift_type, night_shift_type
                    )

                    # Only create a shift if the assigned type matches the current slot type
                    if assigned_shift_type.name != slot_type_name:
                        self.log_debug(f"Squad {squad.name} assigned {assigned_shift_type.name}, but slot is {slot_type_name}. Skipping.")
                        continue

                    # Prepare unique identifier for duplicate checking
                    shift_identifier = (squad.id, slot_start_utc.replace(microsecond=0, tzinfo=pytz.UTC), assigned_shift_type.name)

                    if shift_identifier not in existing_shifts:
                        new_shifts.append(SquadShift(
                            squad=squad,
                            shift_type=assigned_shift_type,
                            shift_start=slot_start_utc,
                            shift_end=slot_end_utc
                        ))
                        generated_count += 1
                        existing_shifts.add(shift_identifier) # Add to set to prevent adding duplicates within this run
                        self.log_debug(f"Added new shift for {squad.name}: {slot_start_utc} ({assigned_shift_type.name})")
                    else:
                        self.log_debug(f"Shift for {squad.name} at {slot_start_utc} ({assigned_shift_type.name}) already exists. Skipping.")

            current_date += timedelta(days=1) # Move to the next day

        self.query_helper.bulk_create_shifts(new_shifts)
        self.log_debug(f"Shift generation complete. Total new shifts created: {generated_count}")
        return generated_count

# --- 6. Django Admin Integration ---
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
        
        # Initialize configuration
        self.config = ShiftGenerationConfig()

        # Initialize helper classes with the configuration
        self.pattern_manager = ShiftPatternManager(self.config)
        self.query_helper = ShiftQueryHelper(self.config)
        self.time_calculator = ShiftTimeCalculator(self.config)

        # Initialize the core generator logic with its dependencies
        self.generator_core = ShiftGeneratorCore(
            self.config,
            self.pattern_manager,
            self.query_helper,
            self.time_calculator
        )
        
        # Apply admin list configurations
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
            try:
                count = self.generator_core.generate_shifts()
                if count > 0:
                    messages.success(request, f"Generated {count} new squad shifts.")
                else:
                    messages.info(request, "No new shifts generated. Schedule may be up to date or no squads found.")
            except Exception as e:
                messages.error(request, f"Error during shift generation: {e}")
                if self.config.DEBUG_ENABLED:
                    print(f"ERROR: {e}") # Print error to console in debug mode
            return redirect('admin:shiftmanagement_squadshift_changelist')

        messages.error(request, "Shift generation requires a POST request.")
        return redirect('admin:shiftmanagement_squadshift_changelist')