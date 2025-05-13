from rest_framework import serializers
from .models import AccrualRates
from employeetype.models import EmployeeType
from payfrequency.models import pay_frequency


class AccuralRateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'accuralrates-detail')
    employee_type = serializers.PrimaryKeyRelatedField(queryset = EmployeeType.objects.all())
    pay_frequency = serializers.PrimaryKeyRelatedField(queryset = pay_frequency.objects.all())
    class Meta:
        model = AccrualRates
        fields = '__all__'

