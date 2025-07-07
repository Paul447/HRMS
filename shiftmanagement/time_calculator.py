from datetime import datetime, timedelta, time
import pytz
from .config import ShiftGenerationConfig

class ShiftTimeCalculator:
    """
    Calculates precise UTC start and end times for shift slots based on
    local timezone rules and predefined shift hours.

    This class handles timezone conversions and determines the appropriate
    starting point for shift generation, ensuring shifts are created
    sequentially and correctly.

    Attributes:
        config (ShiftGenerationConfig): Configuration settings, including
                                         `LOCAL_TIMEZONE`, `REFERENCE_DATE`,
                                         and `DEBUG_ENABLED`.
    """
    def __init__(self, config: ShiftGenerationConfig):
        """
        Initializes the ShiftTimeCalculator with the provided configuration.

        Args:
            config (ShiftGenerationConfig): The configuration object for shift generation.
        """
        self.config = config

    def log_debug(self, message):
        """
        Logs a debug message if debug mode is enabled in the configuration.

        Args:
            message (str): The debug message to log.
        """
        if self.config.DEBUG_ENABLED:
            print(f"[DEBUG] ShiftTimeCalculator: {message}")

    def get_initial_generation_start_utc(self, last_shift_end_utc: datetime | None) -> datetime:
        """
        Determines the appropriate UTC datetime to start generating new shifts from.

        This method checks two scenarios:
        1. If `last_shift_end_utc` is provided (meaning there are existing shifts),
           it calculates the next logical shift start time based on the end time
           of the last shift. It snaps to the next 6 AM or 6 PM local time.
        2. If `last_shift_end_utc` is None (no existing shifts), it uses the
           `REFERENCE_DATE` from the configuration as a starting point and snaps
           to the next 6 AM or 6 PM local time.

        The snapping logic ensures that generation always begins at a valid
        shift start time (6 AM or 6 PM local).

        Args:
            last_shift_end_utc (datetime | None): The UTC end time of the most
                                                   recent existing shift, or None.

        Returns:
            datetime: The calculated UTC datetime representing the earliest
                      point from which new shifts should be generated.
        """
        local_tz = self.config.LOCAL_TIMEZONE
        
        # Determine the base datetime to work from (last shift end or reference date)
        if last_shift_end_utc:
            # Convert last shift end to local timezone for logic
            last_end_local = last_shift_end_utc.astimezone(local_tz)
            last_end_date = last_end_local.date()

            # Logic to find the next 6 AM or 6 PM local time
            if last_end_local.hour < 6:
                # If last shift ended before 6 AM, start generation from 6 AM on the same day
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(6, 0)))
            elif last_end_local.hour < 18:
                # If last shift ended before 6 PM but after 6 AM, start generation from 6 PM on the same day
                next_start_local = local_tz.localize(datetime.combine(last_end_date, time(18, 0)))
            else:
                # If last shift ended after 6 PM, start generation from 6 AM on the next day
                next_start_local = local_tz.localize(datetime.combine(last_end_date + timedelta(days=1), time(6, 0)))
        else:
            # If no last shift, use the configured REFERENCE_DATE as a base
            ref_date_local = self.config.REFERENCE_DATE.astimezone(local_tz)
            if ref_date_local.hour < 6:
                # If reference is before 6 AM, start generation from 6 AM on the reference date
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date(), time(6, 0)))
            elif ref_date_local.hour < 18:
                # If reference is before 6 PM but after 6 AM, start generation from 6 PM on the reference date
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date(), time(18, 0)))
            else:
                # If reference is after 6 PM, start generation from 6 AM on the next day
                next_start_local = local_tz.localize(datetime.combine(ref_date_local.date() + timedelta(days=1), time(6, 0)))
        
        self.log_debug(f"Calculated initial generation start: {next_start_local} (Local)")
        # Convert the calculated local start time to UTC before returning
        return next_start_local.astimezone(pytz.UTC)

    def get_slot_times_utc(self, current_date: datetime.date, hour: int) -> tuple[datetime, datetime, str]:
        """
        Calculates the UTC start and end times for a specific shift slot
        and determines its type (DAY or NIGHT).

        This method assumes 12-hour shifts.
        - A shift starting at 6 AM local time is considered a 'DAY' shift, ending 12 hours later.
        - A shift starting at 6 PM local time is considered a 'NIGHT' shift, ending
          12 hours later (which will be 6 AM on the *next* day).

        Args:
            current_date (datetime.date): The local date for which the shift slot is being calculated.
            hour (int): The starting hour of the shift slot in local time (must be 6 or 18).

        Returns:
            tuple[datetime, datetime, str]: A tuple containing:
                                            - The UTC start datetime of the slot.
                                            - The UTC end datetime of the slot.
                                            - The name of the shift type ('DAY' or 'NIGHT').

        Raises:
            ValueError: If the `hour` is not 6 or 18, as these are the only supported
                        shift start times for this logic.
        """
        local_tz = self.config.LOCAL_TIMEZONE
        
        # Combine the current_date with the specified hour to get the local start datetime
        slot_start_local = local_tz.localize(datetime.combine(current_date, time(hour, 0)))
        
        # Determine end time and slot type based on the hour
        if hour == 6:
            # Day shift: 6 AM to 6 PM on the same day
            slot_end_local = slot_start_local + timedelta(hours=12)
            slot_type_name = 'DAY'
        elif hour == 18:
            # Night shift: 6 PM on current day to 6 AM on the next day
            slot_end_local = local_tz.localize(datetime.combine(current_date + timedelta(days=1), time(6, 0)))
            slot_type_name = 'NIGHT'
        else:
            raise ValueError("Shift hour must be 6 or 18.")
        
        # Convert local times to UTC for database storage and consistency
        slot_start_utc = slot_start_local.astimezone(pytz.UTC)
        slot_end_utc = slot_end_local.astimezone(pytz.UTC)

        self.log_debug(f"Slot: {slot_start_local.strftime('%Y-%m-%d %H:%M %Z%z')} to {slot_end_local.strftime('%Y-%m-%d %H:%M %Z%z')} ({slot_type_name})")
        
        return slot_start_utc, slot_end_utc, slot_type_name