from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile  # Adjust the import as per your model


@receiver(post_save, sender=User)
def create_or_update_experience(sender, instance, created, **kwargs):
    """Automatically create or update experience when a user is created or modified."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()

