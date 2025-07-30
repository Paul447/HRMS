# time_off/filters.py
from django_filters import rest_framework as filters
from timeoffreq.models import TimeoffRequest


class TimeOffRequestFilterSuperUser(filters.FilterSet):
    employee = filters.CharFilter(field_name="employee__user__first_name", lookup_expr="icontains")
    requested_leave_type = filters.CharFilter(field_name="requested_leave_type__leave_type__name", lookup_expr="icontains")

    class Meta:
        model = TimeoffRequest
        fields = ["employee", "requested_leave_type"]
