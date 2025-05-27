from rest_framework import serializers
from .models import PTORequests
import pytz # Used for explicit timezone handling

class PTORequestsSerializer(serializers.ModelSerializer):
    """
    Serializer for the PTORequests model.

    This serializer handles the creation of PTO requests, automatically assigning
    the requesting user and calculating the total duration in hours based on
    start and end datetimes. It explicitly normalizes datetimes to
    the 'America/Chicago' timezone.
    """
    class Meta:
        """
        Meta options for the PTORequestsSerializer.
        """
        model = PTORequests
        # Fields to be included in the serialized output and accepted as input.
        # Note: 'total_hours' is not listed here as it's calculated internally
        # and should typically be added to read_only_fields if it's a model field.
        # Current implementation adds it to validated_data for saving,
        # so it *must* exist on the model.
        fields = ['id', 'start_date_time', 'end_date_time', 'department_name', 'pay_types', 'reason']
        # Fields that are read-only; they will be included in output but cannot
        # be provided or modified by the client during create/update operations.
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to ensure end_date_time is not before start_date_time.
        Also performs timezone normalization and total_hours calculation for both
        create and update operations.
        """
        start_date_time = data.get('start_date_time', self.instance.start_date_time if self.instance else None)
        end_date_time = data.get('end_date_time', self.instance.end_date_time if self.instance else None)

        chicago_tz = pytz.timezone('America/Chicago')

        # Normalize start_date_time
        if start_date_time:
            if start_date_time.tzinfo is None:
                start_date_time = chicago_tz.localize(start_date_time)
            else:
                start_date_time = start_date_time.astimezone(chicago_tz)
        data['start_date_time'] = start_date_time # Update data with normalized value

        # Normalize end_date_time
        if end_date_time:
            if end_date_time.tzinfo is None:
                end_date_time = chicago_tz.localize(end_date_time)
            else:
                end_date_time = end_date_time.astimezone(chicago_tz)
        data['end_date_time'] = end_date_time # Update data with normalized value


        if start_date_time and end_date_time:
            if end_date_time < start_date_time:
                raise serializers.ValidationError("End date and time cannot be before start date and time.")

            # Calculate total_hours
            delta = end_date_time - start_date_time
            data['total_hours'] = round(delta.total_seconds() / 3600.0, 2)
        else:
            data['total_hours'] = 0.0 # Default if dates are not complete or missing

        # Map 'department_name' to 'department' and 'pay_types' to 'pay_type' for saving
        # if they are coming as IDs. This is handled by PrimaryKeyRelatedField in the serializer.
        # So we don't need explicit mapping here if your model fields are `department` and `pay_type`.

        return data

    def create(self, validated_data):
        """
        Custom create method to handle automatic user assignment.
        Timezone normalization and total_hours calculation are now handled in validate.
        """
        # User is assigned by the ViewSet's perform_create method
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Custom update method.
        Timezone normalization and total_hours calculation are now handled in validate.
        """
        # User is assigned by the ViewSet's perform_update method (or checked there)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
