from rest_framework import serializers
from .models import PayType, UserBasedPayType

class PayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayType
        fields = '__all__'

class UserBasedPayTypeSerializer(serializers.ModelSerializer):
    pay_type = PayTypeSerializer(read_only=True)    
    class Meta:
        model = UserBasedPayType
        fields = ['pay_type']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        department_data = rep.pop('pay_type', {})
        rep.update(department_data)
        return rep
    
        