from rest_framework import serializers
from .models import Pay_Frequency


class PayFrequencySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="pay-detail")

    class Meta:
        model = Pay_Frequency
        fields = "__all__"
