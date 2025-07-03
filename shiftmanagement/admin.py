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

@admin.register(SquadShift)
class SquadShiftAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SquadShift model.
    Provides custom functionality for generating shifts based on a predefined pattern.
    """
    list_display = ('id', 'squad', 'shift_type', 'shift_start', 'shift_end')
    list_filter = ('squad', 'shift_type')
    search_fields = ('squad__name', 'shift_type__name')
    ordering = ('shift_start', 'squad__name')

    change_list_template = 'admin/shiftmanagement/squadshift/change_list.html'

    # --- Configuration Constants for Shift Generation ---
    # This defines a 14-day 'on' (1) / 'off' (0) pattern for Squads A & C.
    # Squads B & D will follow the inverse of this pattern for their 'on'/'off' days.
    # Example: if BASE_PATTERN[X] is 1, Squad A and C are 'on'. Squad B and D are 'off'.
    # If BASE_PATTERN[X] is 0, Squad A and C are 'off'. Squad B and D are 'on'.
    BASE_PATTERN = [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0] 

    # A fixed reference date (e.g., a known start of a cycle for Squad A/C).
    # All pattern calculations (day index, 28-day cycle) are relative to this date.
    # It's crucial this remains constant for consistent pattern application across runs.
    # Example: If July 1, 2024, 6 AM UTC is the start of Day 0 for Squad A's pattern.
    REFERENCE_DATE = datetime(2024, 7, 1, 6, 0, 0, tzinfo=pytz.UTC)

    # Local timezone for correct interpretation of 6 AM/6 PM boundaries.
    # IMPORTANT: This should match your Django project's TIME_ZONE setting.
    # We use settings.TIME_ZONE if available, otherwise default.
    LOCAL_TIMEZONE = pytz.timezone(getattr(settings, 'TIME_ZONE', "America/Chicago"))

    # Target number of *new calendar days* for which to generate shifts.
    TARGET_DAYS_TO_GENERATE = 14 
    
    # Maximum iterations to prevent infinite loops (generous safety net).
    # Each iteration processes a 12-hour slot (Day or Night).
    MAX_SLOTS_TO_CHECK = (TARGET_DAYS_TO_GENERATE + 60) * 2 # Added buffer for safety

    # --- Debug Flag ---
    # Set to True to enable verbose print statements during shift generation.
    # REMEMBER TO SET TO False IN PRODUCTION!
    DEBUG_GENERATION = True 

    def _debug_print(self, message):
        """Helper to print messages only if DEBUG_GENERATION is True."""
        if self.DEBUG_GENERATION:
            print(f"[SHIFT_GEN_DEBUG] {message}")

    def get_urls(self):
        """
        Extends the default admin URLs with a custom URL for shift generation.
        """
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
        """
        Custom admin view triggered by the 'Generate Next Shifts' button.
        It orchestrates the shift generation process.
        """
        if request.method == 'POST':
            generated_count = self._generate_shifts_logic()
            if generated_count > 0:
                messages.success(request, f"Successfully generated {generated_count} new squad shifts for the next cycle.")
            else:
                messages.info(request, "No new squad shifts were generated. The schedule might already be up to date or no active squads.")
            return redirect('admin:shiftmanagement_squadshift_changelist')
        
        messages.error(request, "Shift generation requires a POST request via the button.")
        return redirect('admin:shiftmanagement_squadshift_changelist')

    def _get_next_generation_start_time(self):
        """
        Determines the UTC datetime from which new shifts should begin generation.
        This is typically the start of the next 12-hour slot after the last existing shift.
        """
        last_squad_shift = SquadShift.objects.order_by('-shift_end').first()
        
        if last_squad_shift:
            # Convert the last shift's end time to local timezone for boundary calculations.
            last_end_dt_local = last_squad_shift.shift_end.astimezone(self.LOCAL_TIMEZONE)
            
            # Determine the *next* 12-hour slot (6 AM or 6 PM) based on the last shift's end.
            if last_end_dt_local.hour == 6:  # Last shift ended at 6 AM (NIGHT shift), next is 6 AM same day (DAY)
                next_start_dt_local = last_end_dt_local.replace(hour=6, minute=0, second=0, microsecond=0)
            elif last_end_dt_local.hour == 18:  # Last shift ended at 6 PM (DAY shift), next is 6 PM same day (NIGHT)
                next_start_dt_local = last_end_dt_local.replace(hour=18, minute=0, second=0, microsecond=0)
            else:
                # If time is misaligned (shouldn't happen), move to next 6 AM
                next_start_dt_local = (last_end_dt_local + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            
            self._debug_print(f"Last shift ended: {last_end_dt_local} (Local)")
            self._debug_print(f"Next generation calculated to start from: {next_start_dt_local} (Local)")
            return next_start_dt_local.astimezone(pytz.UTC)
        else:
            # If no shifts exist, start from a sensible initial date/time.
            current_year = timezone.now().year
            initial_start_dt_local = self.LOCAL_TIMEZONE.localize(datetime(current_year, 6, 29, 6, 0, 0)) 
            self._debug_print(f"No existing shifts found. Starting generation from: {initial_start_dt_local} (Local)")
            return initial_start_dt_local.astimezone(pytz.UTC)

    def _get_existing_shifts_set(self):
        """
        Fetches existing SquadShift records from the REFERENCE_DATE onwards
        and returns them as a set for efficient duplicate checking.
        The shift_start datetime is normalized to remove microseconds for reliable comparison.
        """
        existing_shifts = SquadShift.objects.filter(
            shift_start__gte=self.REFERENCE_DATE
        ).values_list('squad__id', 'shift_start', 'shift_type__name')
        
        normalized_existing_shifts = set((squad_id, start.replace(microsecond=0), shift_type_name) 
                                         for squad_id, start, shift_type_name in existing_shifts)
        self._debug_print(f"Pre-fetched {len(normalized_existing_shifts)} existing shifts for duplicate check.")
        return normalized_existing_shifts

    def _get_shift_types(self):
        """
        Ensures Day and Night ShiftType objects exist in the database and returns them.
        Creates them if they don't already exist.
        """
        day_shift, created_day = ShiftType.objects.get_or_create(name='DAY')
        night_shift, created_night = ShiftType.objects.get_or_create(name='NIGHT')
        if created_day: self._debug_print("Created new ShiftType: DAY")
        if created_night: self._debug_print("Created new ShiftType: NIGHT")
        return day_shift, night_shift

    def _determine_squad_assignment(self, squad_code, pattern_day_index, is_first_14_days_of_28_cycle, day_shift, night_shift):
        """
        Determines if a squad is 'on' for a given day and which shift type (DAY/NIGHT)
        they are assigned based on the 28-day rotation and 14-day base pattern.
        
        Returns:
            tuple: (is_on_for_day: bool, assigned_shift_type: ShiftType or None)
        """
        # Determine if the current squad is 'on' or 'off' for this day.
        # Squads A & C use BASE_PATTERN directly.
        # Squads B & D use the inverse of BASE_PATTERN.
        is_on_for_day = self.BASE_PATTERN[pattern_day_index] if squad_code in ['A', 'C'] else \
                        (1 - self.BASE_PATTERN[pattern_day_index])

        if not is_on_for_day:
            self._debug_print(f"    Squad {squad_code}: OFF for day index {pattern_day_index}. (Pattern: {self.BASE_PATTERN[pattern_day_index] if squad_code in ['A', 'C'] else (1 - self.BASE_PATTERN[pattern_day_index])})")
            return False, None # This squad is scheduled to be OFF for this day.

        # Determine the specific shift type (DAY/NIGHT) this squad should work.
        # This is based on the 28-day rotation:
        # Squads A & B swap between Day/Night every 14 days.
        # Squads C & D also swap, but inversely to A & B.
        if squad_code in ['A', 'B']: # Squad Group 1
            assigned_shift_type = day_shift if is_first_14_days_of_28_cycle else night_shift
            self._debug_print(f"    Squad {squad_code}: Group 1. First 14 days of 28-day cycle: {is_first_14_days_of_28_cycle}. Assigned: {assigned_shift_type.name}")
        else: # Squad Group 2 (C & D)
            assigned_shift_type = night_shift if is_first_14_days_of_28_cycle else day_shift
            self._debug_print(f"    Squad {squad_code}: Group 2. First 14 days of 28-day cycle: {is_first_14_days_of_28_cycle}. Assigned: {assigned_shift_type.name}")
            
        return True, assigned_shift_type

    def _generate_shifts_logic(self):
        """
        Core logic to generate a rolling schedule of squad shifts for the next `TARGET_DAYS_TO_GENERATE` days.
        """
        self._debug_print("--- Starting Shift Generation Logic ---")
        day_shift, night_shift = self._get_shift_types()
        shifts_to_create = []
        generated_count = 0
        
        earliest_generation_start_dt_utc = self._get_next_generation_start_time()
        existing_squad_shifts_set = self._get_existing_shifts_set()
        all_squads = list(Squad.objects.all())
        if not all_squads:
            self._debug_print("No squads found in the database. Aborting shift generation.")
            return 0
        self._debug_print(f"Found {len(all_squads)} active squads.")

        target_end_dt_utc = earliest_generation_start_dt_utc + timedelta(days=self.TARGET_DAYS_TO_GENERATE)
        self._debug_print(f"Target end date: {target_end_dt_utc.astimezone(self.LOCAL_TIMEZONE)}")

        current_check_dt_utc = earliest_generation_start_dt_utc
        iteration_count = 0

        while current_check_dt_utc < target_end_dt_utc and iteration_count < self.MAX_SLOTS_TO_CHECK:
            iteration_count += 1
            
            target_date_for_pattern = current_check_dt_utc.date()
            days_since_reference = (target_date_for_pattern - self.REFERENCE_DATE.date()).days
            pattern_day_index = days_since_reference % len(self.BASE_PATTERN)
            is_first_14_days_of_28_cycle = (days_since_reference % 28) < 14

            current_slot_local_dt = current_check_dt_utc.astimezone(self.LOCAL_TIMEZONE)
            current_slot_hour = current_slot_local_dt.hour
            current_slot_type_name = 'DAY' if current_slot_hour == 6 else 'NIGHT'

            self._debug_print(f"\n--- Processing Slot: {current_slot_local_dt.strftime('%Y-%m-%d %H:%M %Z%z')} ({current_slot_type_name} Slot) ---")
            self._debug_print(f"  Ref Date: {self.REFERENCE_DATE.date()} | Current Date: {target_date_for_pattern}")
            self._debug_print(f"  Days Since Ref: {days_since_reference} | Pattern Index: {pattern_day_index} | First 14 days of 28-cycle: {is_first_14_days_of_28_cycle}")

            for squad in all_squads:
                self._debug_print(f"  Checking Squad: {squad.name}")
                is_on, assigned_shift_type = self._determine_squad_assignment(
                    squad.name, pattern_day_index, is_first_14_days_of_28_cycle, day_shift, night_shift
                )

                if not is_on:
                    continue 

                if assigned_shift_type.name == current_slot_type_name:
                    self._debug_print(f"    Match! Squad {squad.name} assigned {assigned_shift_type.name} for {current_slot_type_name} slot.")
                    shift_start_final = current_check_dt_utc
                    shift_end_final = current_check_dt_utc + timedelta(hours=12)

                    shift_identifier = (squad.id, shift_start_final.replace(microsecond=0), assigned_shift_type.name)

                    if shift_identifier not in existing_squad_shifts_set:
                        self._debug_print(f"      Shift {squad.name} {assigned_shift_type.name} at {shift_start_final.astimezone(self.LOCAL_TIMEZONE)} NOT found in existing set. Adding to create list.")
                        shifts_to_create.append(SquadShift(
                            squad=squad,
                            shift_type=assigned_shift_type,
                            shift_start=shift_start_final,
                            shift_end=shift_end_final
                        ))
                        generated_count += 1
                        existing_squad_shifts_set.add(shift_identifier)
                    else:
                        self._debug_print(f"      Shift {squad.name} {assigned_shift_type.name} at {shift_start_final.astimezone(self.LOCAL_TIMEZONE)} ALREADY EXISTS. Skipping.")
                else:
                    self._debug_print(f"    NO MATCH. Squad {squad.name} assigned {assigned_shift_type.name}, but slot is {current_slot_type_name}. Skipping.")

            current_check_dt_utc += timedelta(hours=12)

        if shifts_to_create:
            self._debug_print(f"\nAttempting bulk_create for {len(shifts_to_create)} new shifts.")
            SquadShift.objects.bulk_create(shifts_to_create, ignore_conflicts=True)
            self._debug_print("Bulk create completed.")
        else:
            self._debug_print("\nNo shifts to create.")

        self._debug_print(f"--- Shift Generation Finished. Total generated: {generated_count} ---")
        return generated_count