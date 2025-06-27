from rest_framework import serializers
from .models import YearOfExperience, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class YearOfExperienceSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user", write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = YearOfExperience
        fields = "__all__"
