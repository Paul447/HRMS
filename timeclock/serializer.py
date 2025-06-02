# serializers.py
from rest_framework import serializers
from .models import Clock
from payperiod.models import PayPeriod  
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model

class PayPeriodSerializer(serializers.ModelSerializer):
    # Display local dates for better readability in the API response
    start_date_local = serializers.SerializerMethodField()
    end_date_local = serializers.SerializerMethodField()

    class Meta:
        model = PayPeriod
        fields = ['id', 'start_date', 'end_date', 'start_date_local', 'end_date_local']
        read_only_fields = ['start_date', 'end_date'] # Pay periods are created via admin or management command

    def get_start_date_local(self, obj):
        return timezone.localtime(obj.start_date).strftime(' %B %d, %Y - %I:%M %p ')

    def get_end_date_local(self, obj):
        return timezone.localtime(obj.end_date).strftime('%B %d, %Y - %I:%M %p ')


class ClockSerializer(serializers.ModelSerializer):
    # Display the user's username instead of just their ID
    user_username = serializers.CharField(source='user.username', read_only=True)
    # Display local times for clock in/out
    clock_in_time_local = serializers.SerializerMethodField()
    clock_out_time_local = serializers.SerializerMethodField()
    # Serialize the related PayPeriod using its serializer
    pay_period_details = PayPeriodSerializer(source='pay_period', read_only=True)

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