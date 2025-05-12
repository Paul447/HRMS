from rest_framework import serializers
from .models import pay_frequency
from django.contrib.auth.models import User 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class PayFrequencySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    class Meta:
        model = pay_frequency
        fields = ['url','id', 'frequency','user']
        read_only_fields = ['id']

