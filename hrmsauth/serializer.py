from rest_framework import serializers
from django.contrib.auth.models import User, Permission, Group


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     Serializer for the Group model, including permissions.
#     Uses PrimaryKeyRelatedField to list permissions by their IDs.
#     """
#     permissions = serializers.PrimaryKeyRelatedField(
#         queryset=Permission.objects.all(),
#         many=True
#     )

#     class Meta:
#         model = Group
#         fields = '__all__'


# class UserRegisterPermissionSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Permission model, including a hyperlink to each permission detail.
#     """
#     class Meta:
#         model = Permission
#         fields = ['id', 'name']


# class UserRegisterGroupSerializer(serializers.ModelSerializer):
#     """
#     Lightweight serializer for Group registration, only includes ID and name.
#     Useful for dropdowns or assigning groups without full detail.
#     """
#     class Meta:
#         model = Group
#         fields = ['id', 'name']


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     Serializer for the User model with group and permission assignment,
#     password validation, and secure handling of write-only password fields.
#     """
#     url = serializers.HyperlinkedIdentityField(view_name='user-detail')
#     groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
#     user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
#     password = serializers.CharField(write_only=True, required=True)
#     confirm_password = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = [
#             'id', 'url', 'username', 'email', 'is_staff', 'is_superuser',
#             'groups', 'password', 'confirm_password',
#             'user_permissions', 'date_joined', 'last_login'
#         ]
#         depth = 1
#         # read_only_fields = ['last_login']

#     def validate(self, data):
#         """
#         Ensure that password and confirm_password match before creation.
#         """
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError({"password": "Passwords do not match."})
#         return data

#     def create(self, validated_data):
#         """
#         Create a new User instance with hashed password,
#         and assign groups and permissions.
#         """
#         groups = validated_data.pop('groups', [])
#         user_permissions = validated_data.pop('user_permissions', [])
#         password = validated_data.pop('password')
#         validated_data.pop('confirm_password')

#         user = User(**validated_data)
#         user.set_password(password)  # securely hash password
#         user.save()

#         user.groups.set(groups)
#         user.user_permissions.set(user_permissions)
#         return user

#     def update(self, instance, validated_data):
#         """
#         Update user instance with optional password change,
#         group and permission reassignment.
#         """
#         groups = validated_data.pop('groups', [])
#         user_permissions = validated_data.pop('user_permissions', [])
#         password = validated_data.pop('password', None)
#         validated_data.pop('confirm_password', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         if password:
#             instance.set_password(password)

#         instance.save()
#         instance.groups.set(groups)
#         instance.user_permissions.set(user_permissions)
#         return instance
