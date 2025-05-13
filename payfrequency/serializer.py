from rest_framework import serializers
from .models import pay_frequency
from django.contrib.auth.models import User , Permission, Group


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, )
    class Meta:
        model = Group
        fields = '__all__'
        
class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
    user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'url', 'username', 'email', 'is_staff', 'is_superuser',
            'groups', 'password', 'confirm_password',
            'user_permissions', 'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        user.groups.set(groups)
        user.user_permissions.set(user_permissions)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        instance.groups.set(groups)
        instance.user_permissions.set(user_permissions)
        return instance

class PayFrequencySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name = 'pay-detail')
    class Meta:
        model = pay_frequency
        fields = '__all__'

