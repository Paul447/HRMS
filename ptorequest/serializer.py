from rest_framework import serializers
from .models import PTORequests
from department.models import Department
from paytype.models import PayType



class PTORequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTORequests
        fields = ['id', 'user', 'start_date_time', 'end_date_time', 'department_name', 'pay_types', 'status']

   