from .models import EmployeeType
from rest_framework import serializers


class EmployeeTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="employeetype-detail")

    class Meta:
        model = EmployeeType
        fields = "__all__"
