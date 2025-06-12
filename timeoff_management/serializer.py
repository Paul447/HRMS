from rest_framework import serializers
from ptorequest.models import PTORequests
import pytz
from leavetype.models import LeaveType
from department.models import Department, UserProfile
from leavetype.models import DepartmentBasedLeaveType


class TimeOffManagementSerializer(serializers.ModelSerializer):
    """
    Serializer for PTORequests, handling both read and write operations.
    It includes nested serializers for display fields and uses PrimaryKeyRelatedField
    for writeable foreign keys with dynamic queryset filtering.
    """
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


    class Meta:
        model = PTORequests
        fields = [
            'id',
            'department_name_display',
            'leave_type_display',
            'start_date_time',
            'end_date_time',
            'reason',
            'total_hours',
            'status',
        ]
        read_only_fields = ['id','department_name','leave_type', 'department_name_display', 'leave_type_display', 'pay_period_start_date', 'pay_period_end_date', 'total_hours'] 

    

    def update(self, instance, validated_data):
        """
        Updates an existing PTORequest instance.
        The 'total_hours' is automatically calculated in `validate`.
        """
        # Remove display fields as they are not model fields

        return super().update(instance, validated_data)
    