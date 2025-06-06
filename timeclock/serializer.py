# serializers.py
from rest_framework import serializers
from .models import Clock
from django.utils import timezone
from django.contrib.auth import get_user_model
from payperiod.serializer import PayPeriodSerializerForClockPunchReport  # Adjust import based on your project structure



class ClockSerializer(serializers.ModelSerializer):
    # Display the user's username instead of just their ID
    user_username = serializers.CharField(source='user.username', read_only=True)
    # Display local times for clock in/out
    clock_in_time_local = serializers.SerializerMethodField()
    clock_out_time_local = serializers.SerializerMethodField()
    # Serialize the related PayPeriod using its serializer
    pay_period_details = PayPeriodSerializerForClockPunchReport(source='pay_period', read_only=True)

    class Meta:
        model = Clock
        fields = [
            'id', 'user', 'user_username', 'clock_in_time', 'clock_out_time',
            'clock_in_time_local', 'clock_out_time_local',
            'hours_worked', 'pay_period', 'pay_period_details'
        ]
        read_only_fields = ['user', 'hours_worked', 'pay_period'] # User and hours/pay_period are set by backend

    def get_clock_in_time_local(self, obj):
        if obj.clock_in_time:
            return timezone.localtime(obj.clock_in_time).strftime('%a %m/%d %H:%M %p')
        return None

    def get_clock_out_time_local(self, obj):
        if obj.clock_out_time:
            return timezone.localtime(obj.clock_out_time).strftime('%a %m/%d %H:%M %p')
        return None
User = get_user_model()
class ClockSerializerForPunchReport(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Clock
        fields = '__all__' # Or specify fields like ['id', 'user', 'clock_in_time', 'clock_out_time', 'hours_worked', 'pay_period']
        read_only_fields = ['hours_worked'] # Assuming hours_worked is calculated and not set directly by client

# Import the department model to include department details in the serializer


