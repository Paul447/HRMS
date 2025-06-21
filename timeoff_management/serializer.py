from rest_framework import serializers
from ptorequest.models import PTORequests
import pytz


class TimeOffManagementSerializer(serializers.ModelSerializer):
    """
    Serializer for PTORequests, handling both read and write operations.
    It includes nested serializers for display fields and uses PrimaryKeyRelatedField
    for writeable foreign keys with dynamic queryset filtering.
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
            'id',
            'user_first_name',
            'user_last_name',
            'department_name_display',
            'leave_type_display',
            'start_date_time',
            'end_date_time',
            'reason',
            'medical_document',
            'total_hours',
            'status',
        ]
        read_only_fields = ['id','department_name','leave_type', 'department_name_display', 'leave_type_display', 'pay_period_start_date', 'pay_period_end_date', 'total_hours', 'user_first_name', 'user_last_name','start_date_time', 'end_date_time'] 

    

    def update(self, instance, validated_data):
        """
        Updates an existing PTORequest instance.
        """
        # Save the original status before the update for comparison
        # This allows us to check if the status *actually changed*
        instance._original_status = instance.status

        # Perform the actual update using super().update()
        updated_instance = super().update(instance, validated_data)

        # After the update, we can access the new status and the original status
        # This logic will be handled in the perform_update of the ViewSet,
        # but storing original status might be useful for custom serializer logic if needed.

        return updated_instance