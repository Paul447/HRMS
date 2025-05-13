from rest_framework import serializers
from .models import PTOBalance
from employeetype.models import EmployeeType
from payfrequency.models import pay_frequency
from yearofexperience.models import YearOfExperience
from accuralrates.models import AccrualRates


class PTOBalanaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'ptobalance-detail')
    employee_type = serializers.PrimaryKeyRelatedField(queryset=EmployeeType.objects.all())
    pay_frequency = serializers.PrimaryKeyRelatedField(queryset = pay_frequency.objects.all())
    year_of_experience = serializers.PrimaryKeyRelatedField(queryset = YearOfExperience.objects.all())
    class Meta:
        model = PTOBalance
        fields ='__all__'