from rest_framework import serializers
from .models import PayType, DepartmentBasedPayType

class PayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayType
        fields = '__all__'


class DepartmentBasedPayTypeSerializer(serializers.ModelSerializer):
    pay_type = PayTypeSerializer(read_only=True)
    
    class Meta:
        model = DepartmentBasedPayType
        fields = ['pay_type']
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        department_data = rep.pop('pay_type', {})
        rep.update(department_data)
        return rep
    
        