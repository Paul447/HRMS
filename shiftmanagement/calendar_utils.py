from datetime import datetime, time, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from .models import Squad, Employee, SquadShift

class CalendarEventGenerator:
    """Handles generation of calendar events from squad shifts."""
    def __init__(self, local_timezone="America/Chicago"):
        self.local_tz = pytz.timezone(local_timezone)
        self.squad_color_map = {
            'A': '#63b3ed',  # Light Blue
            'B': '#68d391',  # Light Green
            'C': '#f6ad55',  # Orange
            'D': '#fc8181',  # Red
        }

    def get_employees_by_squad(self):
        """Pre-fetch employees grouped by squad for efficient lookup."""
        employees_by_squad = {}
        for squad in Squad.objects.all():
            employees_by_squad[squad.id] = list(
                Employee.objects.filter(squad=squad)
                .select_related('user')
                .order_by('user__username')
            )
        return employees_by_squad

    def create_event(self, squad_shift, start_local, end_local, employees_by_squad):
        """Create a calendar event for a shift or part of a shift."""
        squad_code = squad_shift.squad.name
        event_color = self.squad_color_map.get(squad_code, '#6c757d')  # Default to neutral grey

        squad_members = employees_by_squad.get(squad_shift.squad.id, [])
        employee_names = [emp.user.get_full_name() or emp.user.username for emp in squad_members]
        employee_ids = [emp.id for emp in squad_members]

        return {
            'id': squad_shift.id,
            'title': f"Squad {squad_code} - {squad_shift.shift_type.name}",
            'start': start_local.isoformat(),
            'end': end_local.isoformat(),
            'backgroundColor': event_color,
            'borderColor': event_color,
            'squad_id': squad_shift.squad.id,
            'squad_name': squad_code,
            'shift_type': squad_shift.shift_type.name,
            'employee_names': employee_names,
            'employee_ids': employee_ids,
            'original_start_hour': squad_shift.shift_start.hour,
            'original_end_hour': squad_shift.shift_end.hour,
        }

    def generate_calendar_events(self, squad_shifts_queryset, display_start_date=None, display_end_date=None):
        """
        Generate calendar events, splitting nightshifts across days, from a pre-filtered queryset of SquadShift objects.

        Args:
            squad_shifts_queryset: A Django QuerySet of SquadShift objects, already filtered by DB.
            display_start_date: The start of the date range for which events should be generated (timezone-aware).
            display_end_date: The end of the date range for which events should be generated (timezone-aware).
        """
        employees_by_squad = self.get_employees_by_squad()
        calendar_events = []

        for squad_shift in squad_shifts_queryset:
            shift_start_local = squad_shift.shift_start.astimezone(self.local_tz)
            shift_end_local = squad_shift.shift_end.astimezone(self.local_tz)

            effective_shift_start = max(shift_start_local, display_start_date) if display_start_date else shift_start_local
            effective_shift_end = min(shift_end_local, display_end_date) if display_end_date else shift_end_local

            if effective_shift_start >= effective_shift_end:
                continue

            if shift_start_local.date() < shift_end_local.date():
                midnight_next_day_start = self.local_tz.localize(
                    datetime.combine(shift_start_local.date() + timedelta(days=1), time(0, 0, 0))
                )

                part1_start = shift_start_local
                part1_end = midnight_next_day_start
                part2_start = midnight_next_day_start
                part2_end = shift_end_local

                current_part_start = max(part1_start, display_start_date) if display_start_date else part1_start
                current_part_end = min(part1_end, display_end_date) if display_end_date else part1_end
                if current_part_start < current_part_end:
                    calendar_events.append(
                        self.create_event(
                            squad_shift,
                            start_local=current_part_start,
                            end_local=current_part_end,
                            employees_by_squad=employees_by_squad
                        )
                    )

                current_part_start = max(part2_start, display_start_date) if display_start_date else part2_start
                current_part_end = min(part2_end, display_end_date) if display_end_date else part2_end
                if current_part_start < current_part_end:
                    calendar_events.append(
                        self.create_event(
                            squad_shift,
                            start_local=current_part_start,
                            end_local=current_part_end,
                            employees_by_squad=employees_by_squad
                        )
                    )
            else:
                calendar_events.append(
                    self.create_event(
                        squad_shift,
                        start_local=effective_shift_start,
                        end_local=effective_shift_end,
                        employees_by_squad=employees_by_squad
                    )
                )
        return calendar_events