from rest_framework import serializers
from .models import PTOBalance


class PTOBalanceSerializer(serializers.ModelSerializer):
    employee_type = serializers.ReadOnlyField(source="user.profile.employee_type.name")
    pay_frequency = serializers.ReadOnlyField(source="user.profile.payfreq.frequency")
    accrual_rate = serializers.ReadOnlyField(source="accrual_rate.accrual_rate")
    first_name = serializers.ReadOnlyField(source="user.first_name")
    last_name = serializers.ReadOnlyField(source="user.last_name")

    year_of_experience = serializers.ReadOnlyField(source="user.profile.tenure")
    verified_sick_balance = serializers.DecimalField(source="user.sick_leave_balance.verified_sick_balance", max_digits=5, decimal_places=2, read_only=True)
    unverified_sick_balance = serializers.DecimalField(source="user.sick_leave_balance.unverified_sick_balance", max_digits=5, decimal_places=2, read_only=True)
    used_FVSL = serializers.DecimalField(source="user.sick_leave_balance.used_FVSL", max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = PTOBalance
        fields = ["first_name", "last_name", "employee_type", "pay_frequency", "accrual_rate", "year_of_experience", "pto_balance", "verified_sick_balance", "unverified_sick_balance", "used_FVSL"]
