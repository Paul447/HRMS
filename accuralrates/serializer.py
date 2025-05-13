from rest_framework import serializers
from .models import AccrualRates
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = ['name']
class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pay_Frequency
        fields = ['frequency']

class AccuralRateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'accuralrates-detail')
    employee_type = EmployeeTypeSerializer(read_only=True)
    pay_frequency = PayFrequencySerializer(read_only=True)
    
    employee_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeType.objects.all(),
        source='employee_type',
        write_only=True
    )
    pay_frequency_id = serializers.PrimaryKeyRelatedField(
        queryset=Pay_Frequency.objects.all(),
        source='pay_frequency',
        write_only=True
    )
    class Meta:
        model = AccrualRates
        fields = '__all__'

