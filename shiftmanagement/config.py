from datetime import datetime, timedelta
import pytz

class ShiftGenerationConfig:
    """
    Configuration settings for the shift generation process.

    This class centralizes various parameters that control how shifts are
    generated, including date and time references, target periods, and
    debug options.

    Attributes:
        REFERENCE_DATE (datetime): A fixed UTC datetime used as a reference
                                   point for calculating shift patterns, typically
                                   the start of a known pattern cycle.
        LOCAL_TIMEZONE (pytz.timezone): The local timezone in which shifts
                                        are predominantly managed or displayed.
        TARGET_DAYS (int): The number of days into the future for which shifts
                           should be generated.
        MAX_SLOTS (int): A safety limit representing the maximum number of
                         time slots (e.g., day/night shifts) the generator
                         will attempt to process. This prevents infinite loops
                         in case of logic errors. It's calculated to be
                         sufficiently larger than `TARGET_DAYS * 2` (for day/night slots).
        DEBUG_ENABLED (bool): A flag to enable or disable debug logging
                              throughout the shift generation process.
        BASE_PATTERN (list[int]): A list of integers (0 or 1) representing
                                  a repeating base pattern for squad workdays.
                                  '1' typically means a working day, '0' means off.
                                  This can be customized during initialization.
    """
    # Class-level attributes defining default configuration values
    REFERENCE_DATE = datetime(2025, 7, 14, 6, 0, 0, tzinfo=pytz.UTC)
    LOCAL_TIMEZONE = pytz.timezone('America/Chicago') # Example: US Central Time
    TARGET_DAYS = 14
    MAX_SLOTS = (TARGET_DAYS + 60) * 2  # Safety limit to prevent infinite loops (e.g., 2 shifts per day + buffer)
    DEBUG_ENABLED = True

    def __init__(self, base_pattern=None):
        """
        Initializes the ShiftGenerationConfig.

        Allows for the customization of the `BASE_PATTERN` upon instantiation.

        Args:
            base_pattern (list[int], optional): A custom base shift pattern.
                                                If None, a default pattern is used.
                                                Defaults to None.

        Raises:
            ValueError: If the provided `base_pattern` is empty, or if `TARGET_DAYS`
                        or `MAX_SLOTS` are not positive.
        """
        # Instance-level attribute for the base pattern, allowing it to be overridden
        self.BASE_PATTERN = base_pattern or [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0]
        self.validate() # Validate settings upon initialization

    def validate(self):
        """
        Validates the configuration settings to ensure they are logically sound.

        This method is called during initialization to check for common configuration
        errors that could lead to incorrect behavior or runtime issues.

        Raises:
            ValueError:
                - If `BASE_PATTERN` is empty, as a pattern is required.
                - If `TARGET_DAYS` is not a positive integer, as shifts must be
                  generated for a future period.
                - If `MAX_SLOTS` is not a positive integer, as the safety limit
                  must be meaningful.
        """
        if not self.BASE_PATTERN:
            raise ValueError("BASE_PATTERN must not be empty.")
        if self.TARGET_DAYS <= 0:
            raise ValueError("TARGET_DAYS must be positive.")
        if self.MAX_SLOTS <= 0:
            raise ValueError("MAX_SLOTS must be positive.")