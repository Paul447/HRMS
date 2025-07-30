# Punch Report Views.py
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from django.conf import settings
import pytz
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated
from payperiod.models import PayPeriod
from payperiod.serializer import PayPeriodSerializerForClockPunchReport
from .utils import get_pay_period_week_boundaries, get_user_weekly_summary
from .permissions import IsSelfOrSuperuser


# Create your views here.
class IsSuperuser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class ClockInOutPunchReportView(APIView):
    """
    A view to render the clock in/out punch report page.
    This is a frontend view that will be served to users.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = "clock_in_out_punch_report.html"
    login_url = "hrmsauth:frontend_login"
    versioning_class = None  # Disable versioning for this view

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect(self.login_url)
        return super().handle_exception(exc)

    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)


# views.py



class PunchReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSelfOrSuperuser]

    def list(self, request, *args, **kwargs):
        pay_period_id = request.query_params.get("pay_period_id")

        if not pay_period_id:
            return Response(
                {"detail": "Please provide a 'pay_period_id' query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pay_period = PayPeriod.objects.get(id=pay_period_id)
        except PayPeriod.DoesNotExist:
            return Response(
                {"detail": f"Pay period with ID {pay_period_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        local_tz = pytz.timezone(settings.TIME_ZONE)
        week_boundaries = get_pay_period_week_boundaries(pay_period, local_tz)

        if request.user.is_superuser:
            users_to_report = User.objects.all().order_by("first_name", "last_name")
        else:
            users_to_report = User.objects.filter(id=request.user.id)

        all_users_data = []
        for user_obj in users_to_report:
            # Object-level permission check:
            self.check_object_permissions(request, user_obj)

            user_data = get_user_weekly_summary(user_obj, pay_period, week_boundaries["utc"])
            all_users_data.append({
                "user_id": user_obj.id,
                "username": user_obj.username,
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                **user_data
            })

        return Response({
            "message": "Aggregated clock data for pay period retrieved successfully.",
            "pay_period": PayPeriodSerializerForClockPunchReport(pay_period).data,
            "week_boundaries": week_boundaries["local"],
            "users_clock_data": all_users_data
        }, status=status.HTTP_200_OK)


