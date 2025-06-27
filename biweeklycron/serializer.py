from .models import BiweeklyCron
from rest_framework import serializers


class BiweeklyCronSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="biweeklycron-detail")

    class Meta:
        model = BiweeklyCron
        fields = "__all__"
