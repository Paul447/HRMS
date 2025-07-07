from rest_framework import serializers

class CalendarEventSerializer(serializers.Serializer):
    """
    Serializer for FullCalendar events.
    It takes the flattened event data from CalendarEventGenerator
    and restructures it into FullCalendar's `extendedProps` format.
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    start = serializers.CharField()  # ISO formatted string
    end = serializers.CharField()    # ISO formatted string
    backgroundColor = serializers.CharField()
    borderColor = serializers.CharField()

    squad_id = serializers.IntegerField(write_only=True)
    squad_name = serializers.CharField(write_only=True)
    shift_type = serializers.CharField(write_only=True)
    employee_names = serializers.ListField(child=serializers.CharField(), write_only=True)
    employee_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    original_start_hour = serializers.IntegerField(write_only=True)
    original_end_hour = serializers.IntegerField(write_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['extendedProps'] = {
            'squad_id': instance.get('squad_id'),
            'squad_name': instance.get('squad_name'),
            'shift_type': instance.get('shift_type'),
            'employee_names': instance.get('employee_names', []),
            'employee_ids': instance.get('employee_ids', []),
            'original_start_hour': instance.get('original_start_hour'),
            'original_end_hour': instance.get('original_end_hour'),
        }
        
        for field in [
            'squad_id', 'squad_name', 'shift_type',
            'employee_names', 'employee_ids',
            'original_start_hour', 'original_end_hour'
        ]:
            if field in representation:
                del representation[field]

        return representation
