from rest_framework import serializers
from ptorequest.models import PTORequests
import pytz

class DepartmentLeavesSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing all the leaves in a Department to the Department team members. 
    All the leaves which have the status 'approved' will be displayed. Leaves greater than today's date will be displayed.
    """
    user_first_name = serializers.CharField(
        source='user.first_name',
        read_only=True,
        help_text="First name of the user who made the PTO request."
    )
    user_last_name = serializers.CharField(
        source='user.last_name',
        read_only=True,
        help_text="Last name of the user who made the PTO request."
    )
    department_name_display = serializers.CharField(
        source='department_name.name',
        read_only=True,
        help_text="Display name of the department associated with the PTO request."
    )
    leave_type_display = serializers.CharField(
        source='leave_type.name',
        read_only=True,
        help_text="Display name of the leave type associated with the PTO request."
    )
    start_date_time = serializers.DateTimeField(
        read_only=True,
        help_text="Start date and time of the PTO request.",
        default_timezone=pytz.timezone('America/Chicago'),
        format='%a %m/%d %H:%M %p'  # Optional: specify format if needed
    )
    end_date_time = serializers.DateTimeField(
        read_only=True,
        help_text="End date and time of the PTO request.",
        default_timezone=pytz.timezone('America/Chicago'),
        format='%a %m/%d %H:%M %p'  # Optional: specify format if needed
    )

    class Meta:
        model = PTORequests
        fields = [
            'user_first_name',
            'user_last_name',
            'department_name_display',
            'leave_type_display',
            'start_date_time',
            'end_date_time',
            'total_hours',
            'status',
        ]
        read_only_fields = fields



