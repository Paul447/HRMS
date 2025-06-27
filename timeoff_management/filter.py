# time_off/filters.py
import django_filters
from django_filters import rest_framework as filters
from django.utils import timezone
from timeoffreq.models import TimeoffRequest
from payperiod.models import PayPeriod


class TimeOffRequestFilterSuperUser(filters.FilterSet):
    employee = filters.CharFilter(field_name="employee__user__first_name", lookup_expr="icontains")
    requested_leave_type = filters.CharFilter(field_name="requested_leave_type__leave_type__name", lookup_expr="icontains")

    class Meta:
        model = TimeoffRequest
        fields = ["employee", "requested_leave_type"]
