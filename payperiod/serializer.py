from rest_framework import serializers
from .models import PayPeriod # Adjust import based on where PayPeriod model is

class PayPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPeriod
        fields = '__all__' # Or specify the fields you need, e.g., ['id', 'start_date', 'end_date', 'name']