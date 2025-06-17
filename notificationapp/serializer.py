# notifications_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

# A simple serializer for the User model to avoid exposing sensitive details
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name') # Customize fields as needed

class NotificationSerializer(serializers.ModelSerializer):
    # Serialize the actor and recipient as nested user objects using our public serializer
    actor = UserPublicSerializer(read_only=True)
    recipient = UserPublicSerializer(read_only=True)

    # For the GenericForeignKey (content_object), we'll provide its string representation, ID, and model name.
    # This is a common and simple way to represent GFKs in an API.
    content_object_display = serializers.SerializerMethodField()
    content_object_id = serializers.IntegerField(source='object_id', read_only=True)
    content_type_model = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Notification
        # Specify all fields you want to expose in the API response
        fields = (
            'id', 'actor', 'recipient', 'verb', 'description',
            'content_type_model', 'content_object_id', 'content_object_display',
            'action_url', 'timestamp', 'read', 'level'
        )
        # All these fields are read-only for API consumers. Notifications are created by backend logic.
        read_only_fields = fields

    def get_content_object_display(self, obj):
        """
        Returns the string representation of the related content_object.
        This leverages the __str__ method of the linked model.
        """
        if obj.content_object:
            return str(obj.content_object)
        return None

    # Optional: If you need to include data about the content_object itself,
    # you'd use conditional serialization or a custom field.
    # Example (more complex):
    # content_object_detail = serializers.SerializerMethodField()
    #
    # def get_content_object_detail(self, obj):
    #     if obj.content_object:
    #         if isinstance(obj.content_object, Post): # Assuming you import Post
    #             return PostSerializer(obj.content_object).data
    #         elif isinstance(obj.content_object, Comment): # Assuming you import Comment
    #             return CommentSerializer(obj.content_object).data
    #         # Add more types as needed
    #     return None