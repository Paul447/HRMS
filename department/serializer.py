from rest_framework import serializers
from .models import Department
from .models import UserProfile
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
class UserProfileSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['department', 'is_time_off', 'is_manager']

    def to_representation(self, instance):
        # Get the default representation (with nested department)
        rep = super().to_representation(instance)

        # rep = {'department': {id:..., name:..., ...}}
        department_data = rep.pop('department', {})

        # Merge department_data keys into the top-level rep
        rep.update(department_data)

        return rep