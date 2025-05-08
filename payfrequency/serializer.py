from rest_framework import serializers
from .models import PayFrequency
from django.contrib.auth.models import User 

class PayFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayFrequency
        fields = '__all__'
        
