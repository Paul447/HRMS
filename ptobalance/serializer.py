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
        fields = ["name"]


class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pay_Frequency
        fields = ["frequency"]


class AccuralRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccrualRates
        fields = ["accrual_rate"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class YearOfExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearOfExperience
        fields = ["years_of_experience"]


class PTOBalanceSerializer(serializers.ModelSerializer):
    employee_type = serializers.ReadOnlyField(source="employee_type.name")
    pay_frequency = serializers.ReadOnlyField(source="pay_frequency.frequency")
    accrual_rate = serializers.ReadOnlyField(source="accrual_rate.accrual_rate")
    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")
    year_of_experience = serializers.ReadOnlyField(source="year_of_experience.years_of_experience")
    verified_sick_balance = serializers.DecimalField(source="user.sick_leave_balance.verified_sick_balance", max_digits=5, decimal_places=2, read_only=True)
    unverified_sick_balance = serializers.DecimalField(source="user.sick_leave_balance.unverified_sick_balance", max_digits=5, decimal_places=2, read_only=True)
    used_FVSL = serializers.DecimalField(source="user.sick_leave_balance.used_FVSL", max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = PTOBalance
        fields = ["first_name", "last_name", "employee_type", "pay_frequency", "accrual_rate", "year_of_experience", "pto_balance", "verified_sick_balance", "unverified_sick_balance", "used_FVSL"]
