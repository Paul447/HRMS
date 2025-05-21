from rest_framework import serializers
from .models import PTOBalance
from employeetype.models import EmployeeType
from payfrequency.models import Pay_Frequency
from yearofexperience.models import YearOfExperience
from django.contrib.auth.models import User 
from accuralrates.models import AccrualRates

class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = ['name']
class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pay_Frequency
        fields = ['frequency']

class AccuralRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccrualRates
        fields = ['accrual_rate']
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']
class YearOfExperienceSerializer(serializers.ModelSerializer):
    class Meta: 
        model = YearOfExperience
        fields = ['years_of_experience']

class PTOBalanaceSerializer(serializers.ModelSerializer):
    employee_type = EmployeeTypeSerializer(read_only=True)
    pay_frequency = PayFrequencySerializer(read_only=True)
    accrual_rate = AccuralRateSerializer(read_only = True)
    user = UserSerializer(read_only = True)
    year_of_experience = YearOfExperienceSerializer(read_only = True)
    class Meta:
        model = PTOBalance
        fields = ['employee_type', 'pay_frequency', 'accrual_rate', 'user', 'year_of_experience', 'pto_balance']
    