from rest_framework import serializers
from .models import PayPeriod  # Adjust import based on where PayPeriod model is
from django.utils import timezone


class PayPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPeriod
        fields = "__all__"  # Or specify the fields you need, e.g., ['id', 'start_date', 'end_date', 'name']


class PayPeriodSerializerForClockPunchReport(serializers.ModelSerializer):
    # Display local dates for better readability in the API response
    start_date_local = serializers.SerializerMethodField()
    end_date_local = serializers.SerializerMethodField()

    class Meta:
        model = PayPeriod
        fields = ["id", "start_date", "end_date", "start_date_local", "end_date_local"]
        read_only_fields = ["start_date", "end_date"]  # Pay periods are created via admin or management command

    def get_start_date_local(self, obj):
        return timezone.localtime(obj.start_date).strftime(" %B %d, %Y - %I:%M %p ")

    def get_end_date_local(self, obj):
        return timezone.localtime(obj.end_date).strftime("%B %d, %Y - %I:%M %p ")
