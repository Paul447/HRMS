from rest_framework import serializers
from .models import PayType

class PayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayType
        fields = '__all__'
    
        