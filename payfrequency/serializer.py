from rest_framework import serializers
from .models import pay_frequency
from django.contrib.auth.models import User , Permission, Group

class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
    user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['id']


class PayFrequencySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    class Meta:
        model = pay_frequency
        fields = ['url','id', 'frequency','user']
        read_only_fields = ['id']

