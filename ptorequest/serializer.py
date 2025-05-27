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

    def create(self, validated_data):
        """
        Custom create method to handle automatic field population and calculation.

        This method performs the following:
        1. Assigns the authenticated user to the PTO request.
        2. Normalizes 'start_date_time' and 'end_date_time' to the
           'America/Chicago' timezone, handling both naive and aware inputs.
        3. Calculates the 'total_hours' duration between the normalized datetimes.
        4. Saves the new PTORequests instance to the database.

        Args:
            validated_data (dict): A dictionary of validated data from the request.

        Returns:
            PTORequests: The newly created PTORequests model instance.
        """
        # Define the target timezone for date/time normalization.
        chicago_tz = pytz.timezone('America/Chicago')

        # Automatically assign the currently authenticated user to the PTO request.
        # Assumes 'user' is a ForeignKey on the PTORequests model.
        user = self.context['request'].user
        validated_data['user'] = user

        # Retrieve start and end datetimes from the validated data.
        start_date_time = validated_data.get('start_date_time')
        end_date_time = validated_data.get('end_date_time')

        # --- Timezone Normalization for start_date_time ---
        if start_date_time:
            # If the datetime object is naive (no timezone info), localize it
            # by assuming it's already in the 'America/Chicago' timezone.
            if start_date_time.tzinfo is None:
                start_date_time = chicago_tz.localize(start_date_time)
            # If the datetime object is already timezone-aware, convert it
            # to the 'America/Chicago' timezone.
            else:
                start_date_time = start_date_time.astimezone(chicago_tz)

        # --- Timezone Normalization for end_date_time ---
        if end_date_time:
            # If the datetime object is naive, localize it to 'America/Chicago'.
            if end_date_time.tzinfo is None:
                end_date_time = chicago_tz.localize(end_date_time)
            # If the datetime object is aware, convert it to 'America/Chicago'.
            else:
                end_date_time = end_date_time.astimezone(chicago_tz)

        # Update the validated data with the timezone-normalized datetimes.
        validated_data['start_date_time'] = start_date_time
        validated_data['end_date_time'] = end_date_time

        # Calculate total_hours if both start and end datetimes are present.
        if start_date_time and end_date_time:
            # Calculate the duration (timedelta) between the two datetimes.
            delta = end_date_time - start_date_time
            # Convert the duration to total hours, rounded to two decimal places.
            # This 'total_hours' value will be added to the model instance.
            # Ensure 'total_hours' is a field on your PTORequests model.
            validated_data['total_hours'] = round(delta.total_seconds() / 3600.0, 2)
        else:
            # If either datetime is missing, default total_hours to 0.0.
            # (Consider adding validation to ensure these fields are always present).
            validated_data['total_hours'] = 0.0

        # Call the parent ModelSerializer's create method to save the
        # PTORequests instance with all the prepared validated data.
        return super().create(validated_data)