from rest_framework import serializers
from timeoffreq.models import TimeoffRequest


class DecisionedTimeOffSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
    leave_type = serializers.CharField(source="requested_leave_type.leave_type.name", read_only=True)
    reviewer = serializers.CharField(source="reviewer.get_full_name", read_only=True)
    start_date_time = serializers.DateTimeField(format="%B %d, %Y at %I:%M %p") # Example: "July 26, 2024 at 10:30 AM"
    end_date_time = serializers.DateTimeField(format="%B %d, %Y at %I:%M %p")
    reviewed_at = serializers.DateTimeField(format="%B %d, %Y at %I:%M %p")
    class Meta:
        model = TimeoffRequest
        fields = ["employee_name", "leave_type", "start_date_time", "end_date_time", "status", "document_proof", "employee_leave_reason", "reviewer", "reviewed_at"]
        read_only_fields = fields
