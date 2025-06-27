# notifications_app/models.py
from django.db import models
from django.conf import settings  # Used to reference the User model (AUTH_USER_MODEL)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Custom QuerySet for common notification queries
class NotificationQuerySet(models.QuerySet):
    """
    Custom QuerySet methods for easier notification filtering and management.
    These methods will be available via Notification.objects.
    """

    def for_user(self, user):
        """Filters notifications for a specific recipient user."""
        return self.filter(recipient=user)

    def unread(self, user):
        """Filters unread notifications for a specific recipient user."""
        return self.filter(recipient=user, read=False)

    def read(self, user):
        """Filters read notifications for a specific recipient user."""
        return self.filter(recipient=user, read=True)

    def mark_all_as_read(self, user):
        """Marks all unread notifications for a user as read in one go."""
        # .update() is more efficient than iterating and saving each object
        return self.filter(recipient=user, read=False).update(read=True)

    def mark_all_as_unread(self, user):
        """Marks all read notifications for a user as unread in one go."""
        return self.filter(recipient=user, read=True).update(read=False)


class Notification(models.Model):
    """
    Represents a single notification instance for a user.
    """

    # User who initiated the action (e.g., the user who liked a post)
    # Optional: Can be null if the notification is system-generated.
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="initiated_notifications", help_text="The user or system that initiated the notification.")  # References the User model defined in settings.AUTH_USER_MODEL  # If the actor user is deleted, this field becomes NULL  # How to access notifications where this user is the actor

    # User who receives the notification (e.g., the author of the post that was liked)
    # Required: If the recipient is deleted, their notifications are deleted.
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", help_text="The user who is the intended recipient of the notification.")  # If the recipient user is deleted, delete their notifications  # How to access notifications received by this user (user.notifications.all())

    # A short, concise description of the action (e.g., "liked", "commented on", "followed")
    verb = models.CharField(max_length=255, help_text="A short verb describing the action (e.g., 'liked', 'commented on').")

    # Generic Foreign Key to the object related to the action (e.g., the specific Post that was liked)
    # This allows a notification to refer to *any* model instance.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, help_text="The content type of the related object (e.g., 'Post', 'Comment').")  # References Django's ContentType model (tracks all models in your project)
    object_id = models.PositiveIntegerField(null=True, blank=True, help_text="The primary key of the related object.")
    content_object = GenericForeignKey("content_type", "object_id")
    # This creates the virtual field `content_object` which allows you to get the actual related instance.

    # Optional: A longer, more descriptive message, for richer display on the frontend
    description = models.TextField(blank=True, null=True, help_text="A more detailed description of the notification.")

    # Optional: A URL path for where the notification links to on the frontend
    # (e.g., '/posts/123/' or '/messages/5/')
    action_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL path for the frontend to navigate to when clicking the notification.")

    # Timestamp when the notification was created
    timestamp = models.DateTimeField(auto_now_add=True, help_text="The date and time the notification was created.")  # Automatically sets the timestamp on creation

    # Has the recipient seen/read this notification?
    read = models.BooleanField(default=False, help_text="True if the notification has been read by the recipient.")

    # Optional: A level for visual styling or filtering (e.g., info, warning, error, success)
    LEVEL_CHOICES = [("info", "Info"), ("success", "Success"), ("warning", "Warning"), ("error", "Error")]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="info", help_text="The severity level of the notification.")

    # Use our custom manager
    objects = NotificationQuerySet.as_manager()

    class Meta:
        # Order by newest first by default
        ordering = ["-timestamp"]
        # Essential for query performance
        indexes = [models.Index(fields=["recipient", "read", "-timestamp"]), models.Index(fields=["content_type", "object_id"])]  # Optimize for fetching unread/all notifications for a user  # Optimize for GenericForeignKey lookups
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        """String representation for admin and debugging."""
        actor_name = self.actor.username if self.actor else "System"
        content_obj_str = str(self.content_object) if self.content_object else ""
        return f"To {self.recipient.username}: {actor_name} {self.verb} {content_obj_str}"

    def mark_as_read(self):
        """Convenience method to mark a single notification as read."""
        if not self.read:
            self.read = True
            self.save(update_fields=["read"])  # Only update the 'read' field for efficiency

    def mark_as_unread(self):
        """Convenience method to mark a single notification as unread."""
        if self.read:
            self.read = False
            self.save(update_fields=["read"])  # Only update the 'read' field for efficiency
