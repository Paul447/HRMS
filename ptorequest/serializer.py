from rest_framework import serializers
from .models import PTORequests

class PTORequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTORequests
        fields = ['id',  'start_date_time', 'end_date_time', 'department_name', 'pay_types', 'reason']
        read_only_fields = ['id', 'created_at', 'updated_at']
    def create(self, validated_data):
        # Automatically calculate total_hours on create
        user = self.context['request'].user
        validated_data['user'] = user
        start_date_time = validated_data.get('start_date_time')
        end_date_time = validated_data.get('end_date_time')
        if start_date_time and end_date_time:
            delta = end_date_time - start_date_time
            validated_data['total_hours'] = round(delta.total_seconds() / 3600.0, 2)
        else:
            validated_data['total_hours'] = 0.0
        return super().create(validated_data)

   