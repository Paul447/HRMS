from rest_framework import serializers
# Make sure to import your models correctly
from department.models import Department, UserProfile
from leavetype.models import DepartmentBasedLeaveType
# Note: LeaveType is still implicitly used by DepartmentBasedLeaveType,
# but we don't need a direct serializer for it here.
from payperiod.models import PayPeriod
from django.contrib.auth import get_user_model
from django.utils import timezone
import pytz
from datetime import datetime, timedelta
from .models import TimeoffRequest
from .businesslogicvalidation import validate_pto_request
from django.db import transaction

User = get_user_model()

# --- Nested Serializer for Read Operations for DepartmentBasedLeaveType ---

class DepartmentBasedLeaveTypeReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading DepartmentBasedLeaveType details,
    including a combined 'display_name' for department and leave type.
    """
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = DepartmentBasedLeaveType
        fields = ['id', 'display_name']

    def get_display_name(self, obj):
        """
        Returns the combined string 'Department Name - Leave Type Name'.
        """
        # Ensure that department and leave_type objects are available before accessing their names
        if obj.department and obj.leave_type:
            return f"{obj.department.name} - {obj.leave_type.name}"
        return "N/A - N/A" # Fallback if for some reason related objects are missing

# --- Main TimeoffRequest Serializer ---

class TimeoffRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for TimeoffRequest, handling both read and write operations.
    It includes nested serializers for display fields and uses PrimaryKeyRelatedField
    for writeable foreign keys with dynamic queryset filtering.
    """
    # Read-only fields for displaying related object names/details
    employee_full_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    reviewer_full_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)


    # Use the modified DepartmentBasedLeaveTypeReadSerializer for detailed display
    requested_leave_type_details = DepartmentBasedLeaveTypeReadSerializer(
        source='requested_leave_type', # Points to the ForeignKey on TimeoffRequest
        read_only=True
    )
    
    # Read-only fields for pay period dates
    reference_pay_period_start_date = serializers.DateTimeField(source='reference_pay_period.start_date', read_only=True)
    reference_pay_period_end_date = serializers.DateTimeField(source='reference_pay_period.end_date', read_only=True)

    # Write-only field for accepting primary key of DepartmentBasedLeaveType
    requested_leave_type = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentBasedLeaveType.objects.none(), # Will be set dynamically in __init__
        help_text='ID of the DepartmentBasedLeaveType',
        write_only=True
    )

    class Meta:
        model = TimeoffRequest
        fields = [
            'id',
            'employee',
            'employee_full_name',
            'requested_leave_type',  # For writing the ID
            'requested_leave_type_details', # For reading nested details (now with 'display_name')
            'start_date_time',
            'end_date_time',
            'time_off_duration',
            'employee_leave_reason',
            'status',
            'reference_pay_period', # This can remain, as it's a FK to PayPeriod
            'reference_pay_period_start_date', # Read-only
            'reference_pay_period_end_date',   # Read-only
            'document_proof',
            'created_at',
            'updated_at',
            'reviewer',
            'reviewer_full_name',
            'reviewed_at',
        ]
        read_only_fields = [
            'employee', 'status', 'time_off_duration', 'created_at', 'updated_at',
            'reviewer', 'reviewed_at',
            'reference_pay_period', # Pay period determined by the model's save method
        ]

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters the 'requested_leave_type' queryset
        based on the authenticated user's associated departments
        and their linked DepartmentBasedLeaveTypes.
        """
        super().__init__(*args, **kwargs)

        request_user = self.context.get('request').user if 'request' in self.context else None

        if request_user and request_user.is_authenticated:
            # Get department IDs associated with the user
            # Ensure 'department__id' is used if department is a ForeignKey in UserProfile
            user_department_ids = UserProfile.objects.filter(user=request_user).values_list('department__id', flat=True)
            
            # Filter DepartmentBasedLeaveType instances that belong to the user's departments
            self.fields['requested_leave_type'].queryset = DepartmentBasedLeaveType.objects.filter(
                department__id__in=user_department_ids
            ).select_related('department', 'leave_type') # Optimize query for display_name
        else:
            # If no user or not authenticated, restrict choices
            self.fields['requested_leave_type'].queryset = DepartmentBasedLeaveType.objects.none()

    def _normalize_datetime(self, dt_obj):
        """
        Helper method to normalize a datetime object to the configured timezone (settings.TIME_ZONE).
        """
        if not dt_obj:
            return None

        # Use Django's configured timezone
        target_tz = pytz.timezone(timezone.get_current_timezone().key)
        
        if timezone.is_naive(dt_obj):
            # Assume naive datetimes are local and localize them
            return timezone.make_aware(dt_obj, target_tz)
        else:
            # Convert aware datetimes to the target timezone
            return dt_obj.astimezone(target_tz)

    def validate(self, data):
        """
        Performs custom validation and timezone normalization.
        """
        start_date_time = data.get('start_date_time', self.instance.start_date_time if self.instance else None)
        end_date_time = data.get('end_date_time', self.instance.end_date_time if self.instance else None)

        data['start_date_time'] = self._normalize_datetime(start_date_time)
        data['end_date_time'] = self._normalize_datetime(end_date_time)

        # Re-assign normalized values for validation logic
        start_date_time = data['start_date_time']
        end_date_time = data['end_date_time']

        if start_date_time and end_date_time:
            if end_date_time <= start_date_time:
                raise serializers.ValidationError("End date and time must be after start date and time.")
            
        return data


class TimeoffRequestSerializerEmployee(serializers.ModelSerializer):
    """
    Serializer for TimeoffRequest, tailored for employee stakeholders.
    Handles read and write operations with restricted fields and behavior.
    Includes validation logic from validate_pto_request for leave types (FVSL, UNVSL, VSL).
    """
    # Read-only fields for displaying related object names/details
    employee_full_name = serializers.CharField(source='employee.get_full_name', read_only=True)

    # Nested serializer for reading DepartmentBasedLeaveType details
    requested_leave_type_details = DepartmentBasedLeaveTypeReadSerializer(
        source='requested_leave_type', read_only=True
    )

    # Write-only field for accepting primary key of DepartmentBasedLeaveType
    requested_leave_type = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentBasedLeaveType.objects.none(),
        help_text='ID of the DepartmentBasedLeaveType',
        write_only=True
    )

    class Meta:
        model = TimeoffRequest
        fields = [
            'id', 'employee', 'employee_full_name', 'requested_leave_type',
            'requested_leave_type_details', 'start_date_time', 'end_date_time',
            'time_off_duration', 'employee_leave_reason', 'status', 'document_proof',
        ]
        read_only_fields = [
            'employee', 'status', 'time_off_duration', 'employee_full_name',
            'requested_leave_type_details',
        ]

    def __init__(self, *args, **kwargs):
        """
        Dynamically filters the 'requested_leave_type' queryset based on the
        authenticated user's associated departments.
        """
        super().__init__(*args, **kwargs)
        request_user = self.context.get('request').user if 'request' in self.context else None

        if request_user and request_user.is_authenticated:
            user_department_ids = UserProfile.objects.filter(user=request_user).values_list('department__id', flat=True)
            self.fields['requested_leave_type'].queryset = DepartmentBasedLeaveType.objects.filter(
                department__id__in=user_department_ids
            ).select_related('department', 'leave_type')
        else:
            self.fields['requested_leave_type'].queryset = DepartmentBasedLeaveType.objects.none()

    def _normalize_datetime(self, dt_obj):
        """
        Normalizes a datetime object to the configured timezone.
        """
        if not dt_obj:
            return None
        target_tz = pytz.timezone(timezone.get_current_timezone().key)
        if timezone.is_naive(dt_obj):
            return timezone.make_aware(dt_obj, target_tz)
        return dt_obj.astimezone(target_tz)

    def validate(self, data):
        """
        Performs custom validation, including timezone normalization and leave type-specific checks.
        Uses validate_pto_request for validations (FVSL, UNVSL, VSL).
        """
        # Normalize datetimes
        start_date_time = data.get('start_date_time', self.instance.start_date_time if self.instance else None)
        end_date_time = data.get('end_date_time', self.instance.end_date_time if self.instance else None)
        data['start_date_time'] = self._normalize_datetime(start_date_time)
        data['end_date_time'] = self._normalize_datetime(end_date_time)

        # Hard validation: Ensure end_date_time is after start_date_time
        if data['start_date_time'] and data['end_date_time']:
            if data['end_date_time'] <= data['start_date_time']:
                raise serializers.ValidationError({
                    'end_date_time': "End date and time must be after start date and time."
                })

        # Get leave_type from requested_leave_type
        requested_leave_type = data.get('requested_leave_type', self.instance.requested_leave_type if self.instance else None)
        leave_type = requested_leave_type.leave_type if requested_leave_type else None

        # Call validate_pto_request for leave type-specific validations
        errors = validate_pto_request(
            user=self.context['request'].user,
            leave_type=leave_type,
            start_date_time=data['start_date_time'],
            end_date_time=data['end_date_time'],
            medical_document=data.get('document_proof'),
            instance=self.instance,
            use_select_for_update=False
        )

        if errors:
            raise serializers.ValidationError(errors)

        # Ensure request is for the current pay period
        current_pay_period = PayPeriod.get_pay_period_for_date(timezone.now())
        if not current_pay_period:
            raise serializers.ValidationError({
                'reference_pay_period': "No current pay period found."
            })
        data['reference_pay_period'] = current_pay_period

        return data

    def create(self, validated_data):
        """
        Override create to use select_for_update during balance deduction and set employee.
        """
        with transaction.atomic():
            # Re-validate with use_select_for_update=True
            requested_leave_type = validated_data['requested_leave_type']
            leave_type = requested_leave_type.leave_type
            errors = validate_pto_request(
                user=self.context['request'].user,
                leave_type=leave_type,
                start_date_time=validated_data['start_date_time'],
                end_date_time=validated_data['end_date_time'],
                medical_document=validated_data.get('document_proof'),
                instance=None,
                use_select_for_update=True
            )
            if errors:
                raise serializers.ValidationError(errors)

            # Set employee to authenticated user
            validated_data['employee'] = self.context['request'].user
            return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override update to use select_for_update during balance deduction.
        """
        with transaction.atomic():
            requested_leave_type = validated_data.get('requested_leave_type', instance.requested_leave_type)
            leave_type = requested_leave_type.leave_type
            errors = validate_pto_request(
                user=self.context['request'].user,
                leave_type=leave_type,
                start_date_time=validated_data.get('start_date_time', instance.start_date_time),
                end_date_time=validated_data.get('end_date_time', instance.end_date_time),
                medical_document=validated_data.get('document_proof', instance.document_proof),
                instance=instance,
                use_select_for_update=True
            )
            if errors:
                raise serializers.ValidationError(errors)

            return super().update(instance, validated_data)