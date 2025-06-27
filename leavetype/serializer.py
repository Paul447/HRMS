from rest_framework import serializers
from .models import LeaveType, DepartmentBasedLeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class DepartmentBasedLeaveTypeSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)

    class Meta:
        model = DepartmentBasedLeaveType
        fields = ["leave_type"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        department_data = rep.pop("leave_type", {})
        rep.update(department_data)
        return rep
