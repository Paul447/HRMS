from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Validate that new_password and confirm_new_password match,
        and perform Django's password validation.
        """
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "New passwords must match."})

        # Get the current user from the context (passed from the view)
        user = self.context['request'].user

        # Validate the old password
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Wrong password."})

        # Perform Django's built-in password validation on the new password
        try:
            validate_password(data['new_password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data