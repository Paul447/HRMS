from rest_framework import serializers, viewsets
from rest_framework.response import Response
from django.shortcuts import render
from .models import Squad, Employee, SquadShift # Ensure all models are imported
from datetime import datetime, time, timedelta
import pytz
import json
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

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
        event_color = self.squad_color_map.get(squad_code, '#6c757d') # Default to a neutral grey

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
        Generate calendar events, splitting night shifts across days,
        from a pre-filtered queryset of SquadShift objects.
        
        Args:
            squad_shifts_queryset: A Django QuerySet of SquadShift objects, already filtered by DB.
            display_start_date: The start of the date range for which events should be generated (timezone-aware).
                                Events (or parts of split events) outside this range will be excluded.
            display_end_date: The end of the date range (exclusive or inclusive depending on use)
                              for which events should be generated (timezone-aware).
        """
        employees_by_squad = self.get_employees_by_squad()
        calendar_events = []

        for squad_shift in squad_shifts_queryset: # Iterate over the already filtered queryset
            # All datetimes should be timezone-aware
            shift_start_local = squad_shift.shift_start.astimezone(self.local_tz)
            shift_end_local = squad_shift.shift_end.astimezone(self.local_tz)

            # Determine the actual period of this shift that overlaps with the display range
            effective_shift_start = max(shift_start_local, display_start_date) if display_start_date else shift_start_local
            effective_shift_end = min(shift_end_local, display_end_date) if display_end_date else shift_end_local

            if effective_shift_start >= effective_shift_end: # If no valid overlap, skip
                continue

            # --- Logic for splitting shifts that span midnight ---
            # This check uses the original shift start/end to determine if it truly spans midnight,
            # then generates parts within the effective display range.
            if shift_start_local.date() < shift_end_local.date():
                # Define midnight for the next day, relative to the shift's start date
                # This ensures we get the *correct* midnight for the split.
                midnight_next_day_start = self.local_tz.localize(
                    datetime.combine(shift_start_local.date() + timedelta(days=1), time(0, 0, 0))
                )

                # Part 1: From shift start up to midnight of the next day (24:00:00 of start_date)
                part1_start = shift_start_local
                part1_end = midnight_next_day_start

                # Part 2: From midnight of the next day to shift end
                part2_start = midnight_next_day_start
                part2_end = shift_end_local

                # Check and add Part 1 if it overlaps with the display range
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

                # Check and add Part 2 if it overlaps with the display range
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
                # For shifts that do not span midnight, just add the effective part
                calendar_events.append(
                    self.create_event(
                        squad_shift,
                        start_local=effective_shift_start,
                        end_local=effective_shift_end,
                        employees_by_squad=employees_by_squad
                    )
                )
        return calendar_events

# --- Django Views ---

class ShiftCalendarView(LoginRequiredMixin, TemplateView): # Correctly inherit from TemplateView
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_generator = CalendarEventGenerator()
        
        local_tz = pytz.timezone("America/Chicago") # Ensure timezone is consistent

        # Get current year and month for initial view
        now = datetime.now(local_tz)
        current_year = now.year
        current_month = now.month
        
        # Calculate start and end dates for the current month's display
        start_date_of_month = local_tz.localize(datetime(current_year, current_month, 1, 0, 0, 0))
        end_date_of_month = start_date_of_month + relativedelta(months=1) - timedelta(microseconds=1)
        
        # Initial database query: filter shifts that overlap with the current month view
        # This is passed to the generator to create events only for this subset.
        initial_shifts_queryset = SquadShift.objects.select_related('squad', 'shift_type').filter(
            # shift_start is before or on the last day of the month AND
            shift_start__lt=end_date_of_month + timedelta(days=1),
            # shift_end is after or on the first day of the month
            shift_end__gt=start_date_of_month - timedelta(days=1)
        ).order_by('shift_start')

        # Generate calendar events for the initial month view using the filtered queryset
        calendar_events = event_generator.generate_calendar_events(
            initial_shifts_queryset, 
            display_start_date=start_date_of_month, 
            display_end_date=end_date_of_month
        )
        
        context['calendar_events_json'] = json.dumps(calendar_events)
        context['squads'] = Squad.objects.all().order_by('name')
        context['employees'] = Employee.objects.select_related('user').order_by('user__first_name', 'user__last_name')
        context['squad_color_map'] = event_generator.squad_color_map
        return context

# --- REST Framework Serializers and ViewSets ---

class CalendarEventSerializer(serializers.Serializer):
    """
    Serializer for FullCalendar events.
    It takes the flattened event data from CalendarEventGenerator
    and restructures it into FullCalendar's `extendedProps` format.
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.CharField() # ISO formatted string
    end = serializers.CharField()   # ISO formatted string
    backgroundColor = serializers.CharField()
    borderColor = serializers.CharField()

    squad_id = serializers.IntegerField(write_only=True)
    squad_name = serializers.CharField(write_only=True)
    shift_type = serializers.CharField(write_only=True)
    employee_names = serializers.ListField(child=serializers.CharField(), write_only=True)
    employee_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    original_start_hour = serializers.IntegerField(write_only=True)
    original_end_hour = serializers.IntegerField(write_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['extendedProps'] = {
            'squad_id': instance.get('squad_id'),
            'squad_name': instance.get('squad_name'),
            'shift_type': instance.get('shift_type'),
            'employee_names': instance.get('employee_names', []),
            'employee_ids': instance.get('employee_ids', []),
            'original_start_hour': instance.get('original_start_hour'),
            'original_end_hour': instance.get('original_end_hour'),
        }
        
        for field in [
            'squad_id', 'squad_name', 'shift_type',
            'employee_names', 'employee_ids',
            'original_start_hour', 'original_end_hour'
        ]:
            if field in representation:
                del representation[field]

        return representation

class CalendarEventViewSet(viewsets.ViewSet):
    local_tz = pytz.timezone("America/Chicago")

    def list(self, request):
        event_generator = CalendarEventGenerator(local_timezone=self.local_tz.zone)

        # --- Parse Query Parameters ---
        year_param = request.query_params.get('year')
        month_param = request.query_params.get('month') # This will be None for all_events=true
        squad_id_param = request.query_params.get('squad_id')
        all_events_for_year_flag = request.query_params.get('all_events') == 'true'

        print(f"\n--- API Request Debug ---")
        print(f"Received year_param: {year_param}, month_param: {month_param}, squad_id_param: {squad_id_param}, all_events_for_year_flag: {all_events_for_year_flag}")

        current_year = None
        current_month = None
        display_start_date = None
        display_end_date = None

        try:
            if year_param:
                current_year = int(year_param)
            if month_param:
                current_month = int(month_param)
        except ValueError:
            print("ERROR: Invalid year or month parameter received.")
            return Response({'error': 'Invalid year or month parameter'}, status=400)

        # Default to current month/year if not provided (should be handled by frontend for ICS export)
        if current_year is None: # Current year should *always* be provided for all_events=true
            now = datetime.now(self.local_tz)
            current_year = now.year
            print(f"WARN: Year not provided, defaulting to {current_year}")

        # --- Build Initial QuerySet based on Date Range ---
        shifts_queryset = SquadShift.objects.select_related('squad', 'shift_type').order_by('shift_start')

        if all_events_for_year_flag:
            print("Mode: ALL EVENTS FOR YEAR")
            display_start_date = self.local_tz.localize(datetime(current_year, 1, 1, 0, 0, 0))
            display_end_date = self.local_tz.localize(datetime(current_year, 12, 31, 23, 59, 59, 999999))

            # Filter DB query for shifts that overlap with the entire year
            shifts_queryset = shifts_queryset.filter(
                shift_start__lt=display_end_date + timedelta(days=1), # Filter for shifts starting before (or on) the day after end_date
                shift_end__gt=display_start_date - timedelta(days=1)   # Filter for shifts ending after (or on) the day before start_date
            )
        else: # Standard month-specific view
            print("Mode: MONTH-SPECIFIC")
            if current_month is None: # This case should ideally not happen for month-specific API calls
                now = datetime.now(self.local_tz)
                current_month = now.month
                print(f"WARN: Month not provided for month-specific mode, defaulting to {current_month}")

            display_start_date = self.local_tz.localize(datetime(current_year, current_month, 1, 0, 0, 0))
            display_end_date = display_start_date + relativedelta(months=1) - timedelta(microseconds=1)

            shifts_queryset = shifts_queryset.filter(
                shift_start__lt=display_end_date + timedelta(days=1),
                shift_end__gt=display_start_date - timedelta(days=1)
            )

        print(f"Calculated display_start_date: {display_start_date}")
        print(f"Calculated display_end_date: {display_end_date}")

        # --- Apply Squad Filter ---
        if squad_id_param:
            print(f"Applying squad filter for ID: {squad_id_param}")
            try:
                squad_id_int = int(squad_id_param)
                shifts_queryset = shifts_queryset.filter(squad__id=squad_id_int)
            except ValueError:
                print(f"ERROR: Invalid squad_id parameter: {squad_id_param}")
                return Response({'error': 'Invalid squad_id parameter'}, status=400)
        else:
            print("No squad ID filter applied.")

        # --- Debug QuerySet before Generation ---
        print(f"Initial shifts_queryset count before generation: {shifts_queryset.count()}")
        # print(f"SQL Query: {shifts_queryset.query}") # Uncomment for raw SQL query

        # --- Generate Calendar Events from Filtered QuerySet ---
        calendar_events = event_generator.generate_calendar_events(
            shifts_queryset, 
            display_start_date=display_start_date, 
            display_end_date=display_end_date
        )
        print(f"Generated calendar_events count: {len(calendar_events)}")
        print(f"--- API Request Debug End ---\n")

        # ... (Rest of the list method remains the same) ...
        next_month_dt = self.local_tz.localize(datetime(current_year, current_month, 1)) + relativedelta(months=1)
        prev_month_dt = self.local_tz.localize(datetime(current_year, current_month, 1)) - relativedelta(months=1)

        serializer = CalendarEventSerializer(calendar_events, many=True)
        return Response({
            'calendar_events': serializer.data,
            'squad_color_map': event_generator.squad_color_map,
            'pagination': {
                'current': {'year': current_year, 'month': current_month},
                'next': {'year': next_month_dt.year, 'month': next_month_dt.month},
                'previous': {'year': prev_month_dt.year, 'month': prev_month_dt.month}
            }
        })
    def retrieve(self, request, pk=None):
        event_generator = CalendarEventGenerator(local_timezone=self.local_tz.zone)
        
        try:
            squad_shift = SquadShift.objects.get(pk=pk)
        except SquadShift.DoesNotExist:
            return Response({'error': 'Shift not found'}, status=404)

        # To generate events for a single shift, ensure the display range covers it.
        # Use the shift's own start/end plus a buffer for split shifts.
        shift_start_for_gen = squad_shift.shift_start.astimezone(self.local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        shift_end_for_gen = squad_shift.shift_end.astimezone(self.local_tz).replace(hour=23, minute=59, second=59, microsecond=999999)

        display_start_date = shift_start_for_gen - timedelta(days=1)
        display_end_date = shift_end_for_gen + timedelta(days=1)

        # Pass a queryset containing only this shift to the generator
        shifts_queryset = SquadShift.objects.filter(pk=pk).select_related('squad', 'shift_type')
        all_generated_events = event_generator.generate_calendar_events(
            shifts_queryset, 
            display_start_date=display_start_date, 
            display_end_date=display_end_date
        )
        
        serializer = CalendarEventSerializer(all_generated_events, many=True) # It can be multiple if split
        return Response(serializer.data)