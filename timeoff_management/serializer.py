from rest_framework import serializers
from timeoffreq.models import TimeoffRequest
from timeoffreq.serializer import DepartmentBasedLeaveTypeReadSerializer


class TimeoffApproveRejectManager(serializers.ModelSerializer):
    """
    Serializer for managers to list pending time-off requests and handle approve/reject actions.
    Optimized for read-only listing with minimal fields for approval decisions.
    """

    employee_full_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    requested_leave_type_details = DepartmentBasedLeaveTypeReadSerializer(source="requested_leave_type", read_only=True)

    class Meta:
        model = TimeoffRequest
        fields = ["id", "employee_full_name", "requested_leave_type_details", "start_date_time", "end_date_time", "time_off_duration", "employee_leave_reason", "status", "document_proof"]
        read_only_fields = fields
