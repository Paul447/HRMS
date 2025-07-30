# serializers.py
from rest_framework import serializers
from .models import Clock
from django.utils import timezone
from django.contrib.auth import get_user_model


# This serializer is used for displaying clock data in Clock views, Where users can clock in/out.
class ClockSerializer(serializers.ModelSerializer):
    # Display local times for clock in/out
    clock_in_time_local = serializers.SerializerMethodField()
    clock_out_time_local = serializers.SerializerMethodField()

    class Meta:
        model = Clock
        fields = ["clock_in_time", "clock_out_time","clock_in_time_local", "clock_out_time_local", "hours_worked"]
        read_only_fields = ["user", "hours_worked",]  # User and hours/pay_period are set by backend

    def get_clock_in_time_local(self, obj):
        if obj.clock_in_time:
            return timezone.localtime(obj.clock_in_time).strftime("%a %m/%d %H:%M %p")
        return None

    def get_clock_out_time_local(self, obj):
        if obj.clock_out_time:
            return timezone.localtime(obj.clock_out_time).strftime("%a %m/%d %H:%M %p")
        return None
class ClockSerializerPunch(serializers.ModelSerializer):
    clock_in_time_local = serializers.SerializerMethodField()
    clock_out_time_local = serializers.SerializerMethodField()


    class Meta:
        model = Clock
        fields = [
            "clock_in_time_local",
            "clock_out_time_local",
        ]

    def get_clock_in_time_local(self, obj):
        if obj.clock_in_time:
            return timezone.localtime(obj.clock_in_time).strftime("%a %m/%d %I:%M %p")
        return None

    def get_clock_out_time_local(self, obj):
        if obj.clock_out_time:
            return timezone.localtime(obj.clock_out_time).strftime("%a %m/%d %I:%M %p")
        return None

    def get_duration(self, obj):
        if obj.clock_in_time and obj.clock_out_time:
            delta = obj.clock_out_time - obj.clock_in_time
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes = remainder // 60
            return f"{int(hours)}h {int(minutes)}m"
        return None

# This serializer is used for displaying clock data in punch reports, where detailed clock information is needed.
class ClockSerializerForPunchReportMain(serializers.ModelSerializer):
    """
    Serializer for the Clock model, used for displaying clock data in punch reports.
    It includes user details and formatted clock times.
    """

    clock_in_time_local = serializers.SerializerMethodField()
    clock_out_time_local = serializers.SerializerMethodField()

    class Meta:
        model = Clock
        fields = ["clock_in_time", "clock_out_time", "clock_in_time_local", "clock_out_time_local", "hours_worked", "pay_period"]
        read_only_fields = ["hours_worked"]

    def get_clock_in_time_local(self, obj):
        if obj.clock_in_time:
            return timezone.localtime(obj.clock_in_time).strftime("%a %m/%d %H:%M %p")
        return None

    def get_clock_out_time_local(self, obj):
        if obj.clock_out_time:
            return timezone.localtime(obj.clock_out_time).strftime("%a %m/%d %H:%M %p")
        return None



User = get_user_model()


class ClockSerializerForPunchReport(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Clock
        fields = "__all__"  # Or specify fields like ['id', 'user', 'clock_in_time', 'clock_out_time', 'hours_worked', 'pay_period']
        read_only_fields = ["hours_worked"]  # Assuming hours_worked is calculated and not set directly by client


# Import the department model to include department details in the serializer
