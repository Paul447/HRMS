from .config import ShiftGenerationConfig

class ShiftPatternManager:
    """
    Manages the application of shift patterns to determine if a squad is working
    on a given day and which type of shift (day or night) they are assigned.

    This class encapsulates the logic for mapping a base pattern to specific
    squads and for determining shift types within a broader cycle.

    Attributes:
        config (ShiftGenerationConfig): Configuration settings containing the
                                         `BASE_PATTERN` and other relevant
                                         generation parameters.
    """
    def __init__(self, config: ShiftGenerationConfig):
        """
        Initializes the ShiftPatternManager with the provided configuration.

        Args:
            config (ShiftGenerationConfig): The configuration object for shift generation.
        """
        self.config = config

    def is_squad_working_day(self, squad_code: str, day_index: int) -> bool:
        """
        Determines if a specific squad is scheduled to work on a given day.

        This method uses a `BASE_PATTERN` (e.g., [1, 1, 0, 0, ...]) which is a
        repeating sequence of working (1) or off (0) days. It applies this
        pattern differently based on the `squad_code`:
        - Squads 'A' and 'C' follow the `BASE_PATTERN` directly.
        - Squads 'B' and 'D' work on the inverse of the `BASE_PATTERN` (i.e.,
          when 'A'/'C' are off, 'B'/'D' are on, and vice-versa).

        The `day_index` is used to cycle through the `BASE_PATTERN` using
        the modulo operator (`%`) to ensure it repeats correctly.

        Args:
            squad_code (str): The unique identifier for the squad (e.g., 'A', 'B', 'C', 'D').
            day_index (int): The index of the day relative to the `REFERENCE_DATE`
                             in the configuration (e.g., 0 for reference date, 1 for next day).

        Returns:
            bool: True if the squad is scheduled to work on that day, False otherwise.
        """
        # Calculate the effective index within the repeating BASE_PATTERN
        pattern_value = self.config.BASE_PATTERN[day_index % len(self.config.BASE_PATTERN)]

        # Apply the pattern based on squad code
        if squad_code in ['C', 'D']:
            # Squads C and D work when the pattern value is 1 (True)
            return bool(pattern_value)
        elif squad_code in ['A', 'B']:
            # Squads A and B work when the pattern value is 0 (False - inverse)
            return not bool(pattern_value)
        
        # If squad_code is not recognized, assume they are not working
        return False

    def get_squad_shift_type_for_day(self, squad_code: str, days_since_ref: int,
                                     day_shift_type, night_shift_type):
        """
        Determines whether a squad is assigned a day or night shift for a specific day
        within a 28-day cycle.

        This method implements a specific rule for assigning day/night shifts that
        rotates every 28 days.
        - It calculates a `cycle_number` based on `days_since_ref` divided by 28.
        - If the `cycle_number` is even, squads 'A' and 'B' are assigned night shifts,
          while 'C' and 'D' are assigned day shifts.
        - If the `cycle_number` is odd, squads 'A' and 'B' are assigned day shifts,
          while 'C' and 'D' are assigned night shifts.

        This creates a rotational pattern for day/night assignments among the squads.

        Args:
            squad_code (str): The unique identifier for the squad (e.g., 'A', 'B', 'C', 'D').
            days_since_ref (int): The number of days elapsed since the `REFERENCE_DATE`
                                  in the configuration.
            day_shift_type: The object representing the 'Day' shift type (e.g., from database).
            night_shift_type: The object representing the 'Night' shift type (e.g., from database).

        Returns:
            The `shift_type` object (either `day_shift_type` or `night_shift_type`)
            assigned to the squad for that day.
        """
        # Determine the current 28-day cycle number
        cycle_number = days_since_ref // 28
        
        # Check if it's an "A/B Day Shift" cycle (even cycle_number means A/B get night, C/D get day)
        # This effectively means if cycle_number is even, Squads A and B will have Night shifts, and Squads C and D will have Day shifts.
        # If cycle_number is odd, the roles are reversed.
        is_a_b_day_shift = (cycle_number % 2 == 0)

        if squad_code in ['D', 'B']:
            # For Squads C and D:
            # If it's an "A/B Day Shift" cycle (meaning A/B are on night), C/D get day shift.
            # Otherwise (A/B are on day), C/D get night shift.
            return day_shift_type if is_a_b_day_shift else night_shift_type
        else: # squad_code in ['A', 'B']
            # For Squads A and B:
            # If it's an "A/B Day Shift" cycle (meaning A/B are on night), A/B get night shift.
            # Otherwise (A/B are on day), A/B get day shift.
            return night_shift_type if is_a_b_day_shift else day_shift_type