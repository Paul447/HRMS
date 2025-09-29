from rest_framework import serializers
from unverifiedsickleave.models import SickLeaveBalance
from ptobalance.models import PTOBalance
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class TimeoffBalanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    pto_balance = serializers.DecimalField(
        source="user.pto_balance.pto_balance", max_digits=5, decimal_places=2, read_only=True
    )
    employee_type = serializers.CharField(
        source="user.profile.employee_type.name", read_only=True
    )
    pay_frequency = serializers.CharField(
        source="user.profile.payfreq.frequency", read_only=True
    )
    year_of_experience = serializers.CharField(
        source="user.profile.tenure", read_only=True
    )
    accrual_rate = serializers.CharField(
        source="user.pto_balance.accrual_rate.accrual_rate", read_only=True
    )

    class Meta:
        model = SickLeaveBalance
        fields = [
            "user",
            "unverified_sick_balance",
            "verified_sick_balance",
            "used_FVSL",
            "pto_balance",
            "employee_type",
            "pay_frequency",
            "year_of_experience",
            "accrual_rate",
        ]


