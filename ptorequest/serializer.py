from rest_framework import serializers
from .models import PTORequests
import pytz
from leavetype.models import LeaveType
from department.models import Department, UserProfile
from leavetype.models import DepartmentBasedLeaveType

class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model, used for display purposes.
    """
    class Meta:
        model = Department
        fields = ['id', 'name']

class LeaveTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the LeaveType model, used for display purposes.
    """
    class Meta:
        model = LeaveType
        fields = ['id', 'name']

class PTORequestsSerializer(serializers.ModelSerializer):
    """
    Serializer for PTORequests, handling both read and write operations.
    It includes nested serializers for display fields and uses PrimaryKeyRelatedField
    for writeable foreign keys with dynamic queryset filtering.
    """
    # Read-only fields for displaying related object names
    department_name_display = DepartmentSerializer(source='department_name', read_only=True)
    leave_type_display = LeaveTypeSerializer(source='leave_type', read_only=True)

    # Write-only fields for accepting primary keys for related objects
    department_name = serializers.PrimaryKeyRelatedField(
        # Queryset set to none initially, will be dynamically filtered in __init__
        queryset=Department.objects.none(),
        write_only=True
    )
    leave_type = serializers.PrimaryKeyRelatedField(
        # Queryset set to none initially, will be dynamically filtered in __init__
        queryset=LeaveType.objects.none(),
        write_only=True
    )

    class Meta:
        model = PTORequests
        fields = [
            'id',
            'department_name',
            'department_name_display',
            'leave_type',
            'leave_type_display',
            'start_date_time',
            'end_date_time',
            'reason',
            'total_hours',
            'status',
        ]
        read_only_fields = ['id', 'status', 'total_hours'] # total_hours is calculated, not directly set by client

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters the 'department_name' and 'leave_type' querysets
        based on the authenticated user's associated departments.
        """
        super().__init__(*args, **kwargs)

        request_user = self.context.get('request').user if 'request' in self.context else None

        if request_user and request_user.is_authenticated:
            # Get department IDs associated with the user efficiently
            user_department_ids = UserProfile.objects.filter(user=request_user).values_list('department', flat=True)

            # Filter departments available for the user
            self.fields['department_name'].queryset = Department.objects.filter(id__in=user_department_ids)

            # Filter leave types linked to the user's departments
            linked_leave_type_ids = DepartmentBasedLeaveType.objects.filter(
                department__in=user_department_ids
            ).values_list('leave_type', flat=True)
            self.fields['leave_type'].queryset = LeaveType.objects.filter(id__in=linked_leave_type_ids)
        else:
            # If no user or not authenticated, restrict choices to nothing or handle as per policy
            self.fields['department_name'].queryset = Department.objects.none()
            self.fields['leave_type'].queryset = LeaveType.objects.none()

    def _normalize_datetime(self, dt_obj):
        """
        Helper method to normalize a datetime object to the Chicago timezone.
        """
        if not dt_obj:
            return None

        chicago_tz = pytz.timezone('America/Chicago')
        if dt_obj.tzinfo is None:
            # Assume naive datetimes are in UTC or local server time, then localize to Chicago
            # For robustness, consider if naive datetimes always come in a specific timezone
            # If naive datetimes are *expected* to be in Chicago time but without tzinfo:
            return chicago_tz.localize(dt_obj)
        else:
            # Convert aware datetimes to Chicago timezone
            return dt_obj.astimezone(chicago_tz)

    def validate(self, data):
        """
        Performs custom validation, timezone normalization, and total_hours calculation.
        """
        # Retrieve start and end datetimes, prioritizing new data over existing instance data
        start_date_time = data.get('start_date_time', self.instance.start_date_time if self.instance else None)
        end_date_time = data.get('end_date_time', self.instance.end_date_time if self.instance else None)

        # Normalize datetimes and update data
        data['start_date_time'] = self._normalize_datetime(start_date_time)
        data['end_date_time'] = self._normalize_datetime(end_date_time)

        # Re-assign normalized values for validation logic
        start_date_time = data['start_date_time']
        end_date_time = data['end_date_time']

        if start_date_time and end_date_time:
            if end_date_time < start_date_time:
                raise serializers.ValidationError("End date and time cannot be before start date and time.")

            # Calculate total_hours based on normalized datetimes
            delta = end_date_time - start_date_time
            data['total_hours'] = round(delta.total_seconds() / 3600.0, 2)
        elif start_date_time or end_date_time:
            # If only one date is provided, it's an incomplete range.
            # You might want to add a validation error here or set total_hours to 0.
            # For now, setting to 0 as in your original.
            data['total_hours'] = 0.0
        else:
            data['total_hours'] = 0.0

        return data

    def create(self, validated_data):
        """
        Creates a new PTORequest instance.
        The 'total_hours' is automatically calculated in `validate`.
        User assignment is typically handled by the ViewSet.
        """
        # Remove display fields as they are not model fields
        validated_data.pop('department_name_display', None)
        validated_data.pop('leave_type_display', None)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Updates an existing PTORequest instance.
        The 'total_hours' is automatically calculated in `validate`.
        """
        # Remove display fields as they are not model fields
        validated_data.pop('department_name_display', None)
        validated_data.pop('leave_type_display', None)

        return super().update(instance, validated_data)
    



class PTORequestsListSerializerPunchReport(serializers.ModelSerializer):
    queryset = PTORequests.objects.filter(status='approved').order_by('-start_date_time')
    leave_type_display = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = PTORequests
        fields = [
            'start_date_time',
            'end_date_time',
            'total_hours',
            'leave_type_display',
        ]