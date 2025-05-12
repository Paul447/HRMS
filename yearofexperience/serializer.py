from rest_framework import serializers
from .models import YearOfExperience, User



class YearOfExperienceSerializer(serializers.HyperlinkedModelSerializer):
    user =  serializers.PrimaryKeyRelatedField(queryset = User.objects.all(), many = True)
    class Meta:
        model = YearOfExperience
        fields = '__all__'
        
