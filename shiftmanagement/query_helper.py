from datetime import datetime, timedelta
import pytz
from django.db.models import Q
from .config import ShiftGenerationConfig
from .models import SquadShift, ShiftType, Squad

class ShiftQueryHelper:
    """
    Handles all database-related operations for the shift generation process.

    This class abstracts interactions with the Django ORM, providing methods
    to fetch existing shifts, retrieve or create shift types, get squad data,
    and persist new shifts efficiently.

    Attributes:
        config (ShiftGenerationConfig): Configuration settings, primarily used
                                         for `DEBUG_ENABLED` and `REFERENCE_DATE`.
    """
    def __init__(self, config: ShiftGenerationConfig):
        """
        Initializes the ShiftQueryHelper with the provided configuration.

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
            print(f"[DEBUG] ShiftQueryHelper: {message}")

    def get_last_shift_end_time_utc(self) -> datetime | None:
        """
        Retrieves the end time of the most recently recorded `SquadShift` in the database.

        This is used to determine the starting point for generating new shifts,
        ensuring continuity. The returned datetime object is converted to UTC.

        Returns:
            datetime | None: The UTC `datetime` object of the latest shift's end,
                             or `None` if no shifts exist in the database.
        """
        # Order by 'shift_end' in descending order to get the most recent one
        last_shift = SquadShift.objects.order_by('-shift_end').first()
        if last_shift:
            # Convert the shift_end time to UTC before returning
            self.log_debug(f"Last shift end found: {last_shift.shift_end}")
            return last_shift.shift_end.astimezone(pytz.UTC)
        self.log_debug("No last shift found.")
        return None

    def get_existing_shifts_set(self) -> set[tuple]:
        """
        Fetches a set of identifiers for existing shifts to prevent the creation
        of duplicates during the generation process.

        It queries `SquadShift` objects that started within a recent window
        (defined by `REFERENCE_DATE - 7 days` to ensure relevant shifts are considered).
        Each existing shift is represented as a tuple:
        `(squad_id, shift_start_utc_without_microseconds, shift_type_name)`.
        The `shift_start` time is normalized to UTC and without microseconds for consistent hashing.

        Returns:
            set[tuple]: A set containing unique identifiers for existing shifts.
        """
        # Filter shifts starting from a week before the reference date to capture recent ones
        shifts = SquadShift.objects.filter(
            shift_start__gte=self.config.REFERENCE_DATE - timedelta(days=7)
        ).values_list('squad__id', 'shift_start', 'shift_type__name')

        # Convert the query results into a set of tuples for efficient lookup
        # Normalize datetime objects for consistent comparison (remove microseconds, set tzinfo to UTC)
        shift_set = {
            (squad_id, start.replace(microsecond=0, tzinfo=pytz.UTC), shift_type_name)
            for squad_id, start, shift_type_name in shifts
        }
        self.log_debug(f"Fetched {len(shift_set)} existing shifts.")
        return shift_set

    def get_or_create_shift_types(self) -> tuple:
        """
        Retrieves or creates the standard 'DAY' and 'NIGHT' `ShiftType` objects.

        This ensures that these essential shift types are available in the database
        for assignment to `SquadShift` instances.

        Returns:
            tuple: A tuple containing the 'DAY' `ShiftType` object and the 'NIGHT'
                   `ShiftType` object, respectively.
        """
        day_shift, day_created = ShiftType.objects.get_or_create(name='DAY')
        night_shift, night_created = ShiftType.objects.get_or_create(name='NIGHT')

        if day_created:
            self.log_debug("Created ShiftType: DAY")
        if night_created:
            self.log_debug("Created ShiftType: NIGHT")
            
        return day_shift, night_shift

    def get_all_squads(self) -> list:
        """
        Fetches all `Squad` objects currently in the database.

        Returns:
            list: A list of all `Squad` objects.
        """
        squads = list(Squad.objects.all())
        self.log_debug(f"Found {len(squads)} squads.")
        return squads

    def bulk_create_shifts(self, new_shifts: list):
        """
        Performs a bulk creation of new `SquadShift` instances in the database.

        This method uses Django's `bulk_create` for efficiency, which can
        significantly reduce the number of database queries compared to
        creating each object individually. `ignore_conflicts=True` ensures
        that if a shift with the same unique constraints already exists (though
        the `get_existing_shifts_set` logic should largely prevent this), it
        will not cause an error.

        Args:
            new_shifts (list[SquadShift]): A list of `SquadShift` objects to be created.
        """
        if new_shifts:
            self.log_debug(f"Attempting to bulk create {len(new_shifts)} new shifts.")
            # Use bulk_create for efficient insertion of multiple objects
            SquadShift.objects.bulk_create(new_shifts, ignore_conflicts=True)
            self.log_debug("Bulk creation completed.")
        else:
            self.log_debug("No new shifts to bulk create.")