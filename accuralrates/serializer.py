from rest_framework import serializers
from .models import AccrualRates
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = '__all__'

class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pay_Frequency
        fields = '__all__'

class AccuralRateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'accuralrates-detail')
    employee_type = EmployeeTypeSerializer(read_only=True)
    pay_frequency = PayFrequencySerializer(read_only=True)
    class Meta:
        model = AccrualRates
        fields = '__all__'

