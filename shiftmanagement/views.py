# shiftmanagement/views.py

from django.shortcuts import render
from django.utils import timezone
import pytz
import json
# Import SquadShift instead of ShiftAssignment
from .models import SquadShift, Employee, Squad, ShiftType 

def shift_calendar_view(request):
    # Query SquadShift objects
    squad_shifts = SquadShift.objects.select_related(
        'squad',
        'shift_type'
    ).all().order_by('shift_start')

    calendar_events = []
    local_tz = pytz.timezone("America/Chicago")

    squad_color_map = {
        'A': '#4CAF50', # Green
        'B': '#2196F3', # Blue
        'C': '#FF9800', # Orange
        'D': '#E91E63', # Pink
    }

    # Pre-fetch all employees grouped by squad for efficient lookup
    employees_by_squad = {}
    for squad in Squad.objects.all():
        employees_by_squad[squad.id] = list(Employee.objects.filter(squad=squad).select_related('user').order_by('user__username'))

    for squad_shift in squad_shifts:
        shift_start_local = squad_shift.shift_start.astimezone(local_tz)
        shift_end_local = squad_shift.shift_end.astimezone(local_tz)

        squad_code = squad_shift.squad.name
        event_color = squad_color_map.get(squad_code, '#607D8B')

        # Get employees for this squad to display in the event title/tooltip
        squad_members = employees_by_squad.get(squad_shift.squad.id, [])
        employee_names = [emp.user.get_full_name() or emp.user.username for emp in squad_members]
        
        # Create a more descriptive title for the squad shift
        title = f"Squad {squad_code} - {squad_shift.shift_type.name}"
        if employee_names:
            title += f" ({', '.join(employee_names)})" # List all employees in the title

        calendar_events.append({
            'id': squad_shift.id,
            'title': title,
            'start': shift_start_local.isoformat(),
            'end': shift_end_local.isoformat(),
            'backgroundColor': event_color,
            'borderColor': event_color,
            'extendedProps': {
                'squad_id': squad_shift.squad.id,
                'squad_name': squad_code,
                'shift_type': squad_shift.shift_type.name,
                'employee_names': employee_names, # Pass list of employee names
                'employee_ids': [emp.id for emp in squad_members], # Pass list of employee IDs for filtering
            }
        })
    
    all_squads = Squad.objects.all().order_by('name')
    all_employees = Employee.objects.select_related('user').all().order_by('user__first_name', 'user__last_name')

    context = {
        'calendar_events_json': json.dumps(calendar_events),
        'squads': all_squads,
        'employees': all_employees,
        'squad_color_map': squad_color_map
    }
    return render(request, 'shiftmanagement/calendar.html', context)