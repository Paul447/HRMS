from datetime import timedelta
import pytz
from .config import ShiftGenerationConfig
from .pattern_manager import ShiftPatternManager
from .query_helper import ShiftQueryHelper
from .time_calculator import ShiftTimeCalculator
from .models import SquadShift

class ShiftGeneratorCore:
    """
    Manages the creation of new shifts for squads based on a defined schedule and patterns.

    This class orchestrates the entire shift generation process, from determining the
    generation period to identifying which squads are working, calculating shift
    times, and persisting new shifts to the database.

    Attributes:
        config (ShiftGenerationConfig): Configuration settings for shift generation,
                                         including debug mode, target days, and timezones.
        pattern_manager (ShiftPatternManager): Manages shift patterns for squads,
                                                determining working days and assigned shift types.
        query_helper (ShiftQueryHelper): Handles database interactions, such as
                                          fetching shift types, squads, and existing shifts,
                                          and performing bulk creation of new shifts.
        time_calculator (ShiftTimeCalculator): Provides utility methods for calculating
                                                shift start/end times and initial generation
                                                start dates, handling timezone conversions.
    """
    def __init__(self, config: ShiftGenerationConfig,
                 pattern_manager: ShiftPatternManager,
                 query_helper: ShiftQueryHelper,
                 time_calculator: ShiftTimeCalculator):
        """
        Initializes the ShiftGeneratorCore with necessary dependencies.

        Args:
            config (ShiftGenerationConfig): Configuration settings.
            pattern_manager (ShiftPatternManager): Manager for shift patterns.
            query_helper (ShiftQueryHelper): Helper for database queries.
            time_calculator (ShiftTimeCalculator): Calculator for time-related operations. 
        """
        self.config = config
        self.pattern_manager = pattern_manager
        self.query_helper = query_helper
        self.time_calculator = time_calculator

    def log_debug(self, message):
        """
        Logs a debug message if debug mode is enabled in the configuration.

        Args:
            message (str): The debug message to log.
        """
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] ShiftGeneratorCore: {message}")

    def generate_shifts(self) -> int:
        """
        Generates new shifts for a specified target period based on squad patterns.

        The process involves:
        1. Retrieving or creating default day and night shift types.
        2. Fetching all active squads. If no squads are found, the generation
           process is aborted.
        3. Identifying all existing shifts to prevent duplicates.
        4. Determining the starting point for shift generation, typically from
           the end of the last recorded shift or a predefined reference.
        5. Iterating through each day and predefined shift hours (e.g., 6 AM, 6 PM)
           within the target generation period.
        6. For each potential shift slot, it checks:
           a. If the squad is scheduled to work on that specific day according to its pattern.
           b. If the assigned shift type for the squad on that day matches the current
              time slot (e.g., a day shift squad for a 6 AM slot).
           c. If a shift with the same squad, start time, and type already exists.
        7. If all conditions are met and the shift is new, a new `SquadShift` object
           is created and added to a list.
        8. Finally, all newly generated shifts are bulk-created in the database.

        Returns:
            int: The total number of new shifts successfully generated and created.
        """
        self.log_debug("Starting shift generation process.")

        # 1. Retrieve or create default shift types (Day/Night)
        day_shift_type, night_shift_type = self.query_helper.get_or_create_shift_types()

        # 2. Fetch all active squads
        squads = self.query_helper.get_all_squads()
        if not squads:
            self.log_debug("No squads found. Aborting shift generation.")
            return 0

        # 3. Get a set of existing shifts for efficient lookup to avoid duplicates
        existing_shifts = self.query_helper.get_existing_shifts_set()

        # 4. Determine the starting point for shift generation
        last_shift_end_utc = self.query_helper.get_last_shift_end_time_utc()
        start_generation_dt_utc = self.time_calculator.get_initial_generation_start_utc(last_shift_end_utc)

        # Calculate the local start date and the end date for generation
        start_date_local = start_generation_dt_utc.astimezone(self.config.LOCAL_TIMEZONE).date()
        end_date = start_date_local + timedelta(days=self.config.TARGET_DAYS)
        self.log_debug(f"Generating shifts from {start_date_local} to {end_date}.")

        new_shifts = []
        generated_count = 0
        iteration_count = 0
        current_date = start_date_local

        # 5. Iterate through each day within the target period
        while current_date < end_date and iteration_count < self.config.MAX_SLOTS:
            # 6. For each day, iterate through predefined shift hours (e.g., 6 AM for day, 6 PM for night)
            for hour in [6, 18]: # Assuming 6 AM for day shift start, 6 PM for night shift start
                iteration_count += 1
                # Calculate the UTC start and end times for the current slot and its type (Day/Night)
                slot_start_utc, slot_end_utc, slot_type_name = \
                    self.time_calculator.get_slot_times_utc(current_date, hour)
                
                # Calculate days since the reference date to use with shift patterns
                days_since_ref = (current_date - self.config.REFERENCE_DATE.date()).days

                # Iterate through each squad
                for squad in squads:
                    # 6a. Check if the squad is working on the current day based on its pattern
                    if not self.pattern_manager.is_squad_working_day(squad.name, days_since_ref):
                        self.log_debug(f"Squad {squad.name} is OFF on {current_date.strftime('%Y-%m-%d')}.")
                        continue

                    # Determine the specific shift type (Day/Night) assigned to the squad for this day
                    assigned_shift_type = self.pattern_manager.get_squad_shift_type_for_day(
                        squad.name, days_since_ref, day_shift_type, night_shift_type
                    )

                    # 6b. Check if the assigned shift type matches the current time slot's type
                    if assigned_shift_type.name != slot_type_name:
                        self.log_debug(f"Squad {squad.name} assigned {assigned_shift_type.name}, but slot is {slot_type_name}. Skipping.")
                        continue

                    # Create a unique identifier for the potential shift to check for existence
                    # Microseconds are set to 0 and tzinfo to UTC for consistent hashing
                    shift_identifier = (squad.id, slot_start_utc.replace(microsecond=0, tzinfo=pytz.UTC), assigned_shift_type.name)

                    # 6c. Check if a similar shift already exists
                    if shift_identifier not in existing_shifts:
                        # 7. If the shift is new, create a SquadShift object and add it to the list
                        new_shifts.append(SquadShift(
                            squad=squad,
                            shift_type=assigned_shift_type,
                            shift_start=slot_start_utc,
                            shift_end=slot_end_utc
                        ))
                        generated_count += 1
                        # Add to existing_shifts set immediately to prevent duplicates within the same run
                        existing_shifts.add(shift_identifier)
                        self.log_debug(f"Added new shift for {squad.name}: {slot_start_utc} ({assigned_shift_type.name})")
                    else:
                        self.log_debug(f"Shift for {squad.name} at {slot_start_utc} ({assigned_shift_type.name}) already exists. Skipping.")
            
            # Move to the next day
            current_date += timedelta(days=1)
        
        # 8. Bulk create all newly generated shifts in the database
        self.query_helper.bulk_create_shifts(new_shifts)
        self.log_debug(f"Shift generation complete. Total new shifts created: {generated_count}")
        return generated_count