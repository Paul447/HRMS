from rest_framework import viewsets
from rest_framework.response import Response
from .models import Squad, Employee, SquadShift
from .calendar_utils import CalendarEventGenerator
from .serializers import CalendarEventSerializer
import json
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from department.models import UserProfile
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.shortcuts import redirect

class IsLawEnforcementDepartment(BasePermission):
    """
    Custom permission to only allow users from the Law Enforcement department.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return user_profile.department.name == "Law Enforcement"
        except UserProfile.DoesNotExist:
            return False

class ShiftCalendarView(APIView):
    template_name = 'calendar.html'
    renderer_classes = [TemplateHTMLRenderer]
    login_url = 'frontend_login'

    def get_permissions(self):
        if self.request.user.is_superuser:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLawEnforcementDepartment()]

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return Response(context, template_name=self.template_name)

    def get_context_data(self, **kwargs):
        context = {}
        event_generator = CalendarEventGenerator()
        
        local_tz = pytz.timezone("America/Chicago")
        now = timezone.now().astimezone(local_tz)
        current_year, current_month = now.year, now.month
        
        start_date = local_tz.localize(datetime(current_year, current_month, 1))
        end_date = start_date + relativedelta(months=1) - timezone.timedelta(microseconds=1)
        
        shifts = SquadShift.objects.select_related('squad', 'shift_type').filter(
            shift_start__lt=end_date + timezone.timedelta(days=1),
            shift_end__gt=start_date - timezone.timedelta(days=1)
        ).order_by('shift_start')

        events = event_generator.generate_calendar_events(
            shifts, display_start_date=start_date, display_end_date=end_date
        )
        
        context.update({
            'calendar_events_json': json.dumps(events),
            'squads': Squad.objects.all().order_by('name'),
            'employees': Employee.objects.select_related('user').order_by('user__first_name', 'user__last_name'),
            'squad_color_map': event_generator.squad_color_map
        })
        return context


class CalendarEventViewSet(viewsets.ViewSet):
    local_tz = pytz.timezone("America/Chicago")

    def get_permissions(self):
        if self.request.user.is_superuser:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsLawEnforcementDepartment()]

    def list(self, request):
        event_generator = CalendarEventGenerator(local_timezone=self.local_tz.zone)

        year_param = request.query_params.get('year')
        month_param = request.query_params.get('month')
        squad_id_param = request.query_params.get('squad_id')
        all_events_for_year_flag = request.query_params.get('all_events') == 'true'

        

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

        if current_year is None:
            now = timezone.now().astimezone(self.local_tz)
            current_year = now.year
            print(f"WARN: Year not provided, defaulting to {current_year}")

        shifts_queryset = SquadShift.objects.select_related('squad', 'shift_type').order_by('shift_start')

        if all_events_for_year_flag:
            print("Mode: ALL EVENTS FOR YEAR")
            display_start_date = self.local_tz.localize(datetime(current_year, 1, 1, 0, 0, 0))
            display_end_date = self.local_tz.localize(datetime(current_year, 12, 31, 23, 59, 59, 999999))

            shifts_queryset = shifts_queryset.filter(
                shift_start__lt=display_end_date + timezone.timedelta(days=1),
                shift_end__gt=display_start_date - timezone.timedelta(days=1)
            )
        else:
            print("Mode: MONTH-SPECIFIC")
            if current_month is None:
                now = timezone.now().astimezone(self.local_tz)
                current_month = now.month
                print(f"WARN: Month not provided for month-specific mode, defaulting to {current_month}")

            display_start_date = self.local_tz.localize(datetime(current_year, current_month, 1, 0, 0, 0))
            display_end_date = display_start_date + relativedelta(months=1) - timezone.timedelta(microseconds=1)

            shifts_queryset = shifts_queryset.filter(
                shift_start__lt=display_end_date + timezone.timedelta(days=1),
                shift_end__gt=display_start_date - timezone.timedelta(days=1)
            )

        print(f"Calculated display_start_date: {display_start_date}")
        print(f"Calculated display_end_date: {display_end_date}")

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

        print(f"Initial shifts_queryset count before generation: {shifts_queryset.count()}")

        calendar_events = event_generator.generate_calendar_events(
            shifts_queryset, 
            display_start_date=display_start_date, 
            display_end_date=display_end_date
        )
       

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

        shift_start_for_gen = squad_shift.shift_start.astimezone(self.local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        shift_end_for_gen = squad_shift.shift_end.astimezone(self.local_tz).replace(hour=23, minute=59, second=59, microsecond=999999)

        display_start_date = shift_start_for_gen - timezone.timedelta(days=1)
        display_end_date = shift_end_for_gen + timezone.timedelta(days=1)

        shifts_queryset = SquadShift.objects.filter(pk=pk).select_related('squad', 'shift_type')
        all_generated_events = event_generator.generate_calendar_events(
            shifts_queryset, 
            display_start_date=display_start_date, 
            display_end_date=display_end_date
        )
        
        serializer = CalendarEventSerializer(all_generated_events, many=True)
        return Response(serializer.data)