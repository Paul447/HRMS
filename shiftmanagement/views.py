from django.shortcuts import render
import json
import pytz
from datetime import datetime, timedelta, time
from .models import Squad, SquadShift, Employee

class CalendarEventGenerator:
    """Handles generation of calendar events from squad shifts."""
    def __init__(self, local_timezone="America/Chicago"):
        self.local_tz = pytz.timezone(local_timezone)
        self.squad_color_map = {
            'A': 'rgb(66, 255, 113)',  # Vivid green
            'B': 'rgba(219, 160, 131, 0.72)',  # Bright blue
            'C': 'rgb(228, 181, 98)',  # Warm amber
            'D': 'rgba(72, 236, 228, 0.8)',  # Vivid pink
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
        event_color = self.squad_color_map.get(squad_code, '#607D8B')
        squad_members = employees_by_squad.get(squad_shift.squad.id, [])
        employee_names = [emp.user.get_full_name() or emp.user.username for emp in squad_members]
        
        title = f"Squad {squad_code} - {squad_shift.shift_type.name}"
        if employee_names:
            title += f" ({', '.join(employee_names)})"

        return {
            'id': squad_shift.id,
            'title': title,
            'start': start_local.isoformat(),
            'end': end_local.isoformat(),
            'backgroundColor': event_color,
            'borderColor': event_color,
            'extendedProps': {
                'squad_id': squad_shift.squad.id,
                'squad_name': squad_code,
                'shift_type': squad_shift.shift_type.name,
                'employee_names': employee_names,
                'employee_ids': [emp.id for emp in squad_members],
            }
        }

    def generate_calendar_events(self):
        """Generate calendar events, splitting night shifts across days."""
        squad_shifts = SquadShift.objects.select_related('squad', 'shift_type').order_by('shift_start')
        employees_by_squad = self.get_employees_by_squad()
        calendar_events = []

        for squad_shift in squad_shifts:
            shift_start_local = squad_shift.shift_start.astimezone(self.local_tz)
            shift_end_local = squad_shift.shift_end.astimezone(self.local_tz)

            if shift_start_local.hour == 18 and shift_end_local.hour == 6:
                midnight = self.local_tz.localize(
                    datetime.combine(shift_start_local.date() + timedelta(days=1), time(0, 0))
                )
                calendar_events.append(
                    self.create_event(
                        squad_shift,
                        start_local=shift_start_local,
                        end_local=midnight,
                        employees_by_squad=employees_by_squad
                    )
                )
                calendar_events.append(
                    self.create_event(
                        squad_shift,
                        start_local=midnight,
                        end_local=shift_end_local,
                        employees_by_squad=employees_by_squad
                    )
                )
            else:
                calendar_events.append(
                    self.create_event(
                        squad_shift,
                        start_local=shift_start_local,
                        end_local=shift_end_local,
                        employees_by_squad=employees_by_squad
                    )
                )

        return calendar_events

def shift_calendar_view(request):
    """View for rendering the shift calendar."""
    event_generator = CalendarEventGenerator()
    calendar_events = event_generator.generate_calendar_events()
    
    context = {
        'calendar_events_json': json.dumps(calendar_events),
        'squads': Squad.objects.all().order_by('name'),
        'employees': Employee.objects.select_related('user').order_by('user__first_name', 'user__last_name'),
        'squad_color_map': event_generator.squad_color_map
    }
    return render(request, 'shiftmanagement/calendar.html', context)