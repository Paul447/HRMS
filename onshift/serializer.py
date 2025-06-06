from rest_framework import serializers
from django.utils import timezone
from timeclock.models import Clock

class UserOnShiftClockSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a user's current clock entry if they are on shift.
    """
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    department = serializers.CharField(source='user.userprofile.department.name', read_only=True)
    clock_in_time_local = serializers.SerializerMethodField()

    class Meta:
        model = Clock
        fields = ['user', 'first_name', 'last_name', 'department', 'clock_in_time', 'clock_in_time_local']
        read_only_fields = ['user']

    def get_clock_in_time_local(self, obj):
        return timezone.localtime(obj.clock_in_time).strftime('%a %m/%d %H:%M %p') if obj.clock_in_time else None