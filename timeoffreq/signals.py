# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.contenttypes.models import ContentType
# from department.models import UserProfile
# from ptorequest.models import PTORequests
# from notificationapp.models import Notification

# @receiver(post_save, sender=PTORequests)
# def create_notification(sender, instance, created, **kwargs):
#  # Or raise an exception or handle accordingly
#     if created:
#         requester = instance.user
#         requester_profile = UserProfile.objects.filter(user=requester).first()

#         if requester_profile:
#             department = requester_profile.department
#             department_supervisor = UserProfile.objects.filter(department=department, is_manager=True).first()
#         else:
#             department_supervisor = None


#         if department_supervisor: # ONLY create notification if a supervisor is found
#             Notification.objects.create(
#                 actor=instance.user,
#                 recipient=department_supervisor,
#                 verb='Time Off request',
#                 content_type=ContentType.objects.get_for_model(instance),
#                 object_id=instance.id,
#                 description=f"{instance.user.username} has created a Time Off request."
#             )
#         else:
#             # IMPORTANT: Log this situation!
#             # This tells you when a PTO request is made without a clear recipient.
#             print(f"WARNING: PTO request from {requester.username} has no designated supervisor recipient.")
#         # Or use Django's logging system:
#         # import logging
#         # logger = logging.getLogger(__name__)
#         # logger.warning(f"PTO request from {requester.username} has no designated supervisor recipient.")

# ptorequest/signals.py
import os
import shutil # For deleting directories
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import TimeoffRequest # Import your TimeoffRequest model

@receiver(post_delete, sender=TimeoffRequest)
def delete_pto_document_and_folder(sender, instance, **kwargs):
    """
    Deletes medical document file and its containing user folder when
    the associated TimeoffRequest instance is deleted.
    """
    if instance.document_proof:
        # Get the absolute path to the file
        file_path = instance.document_proof.path
        
        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}") # For debugging
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")
        else:
            print(f"File not found, skipping deletion: {file_path}")

        # Now, attempt to remove the parent directory if it's empty
        # This assumes your upload_to function creates a user-specific folder directly under 'timeoff_documents'
        # e.g., MEDIA_ROOT/timeoff_documents/john_doe-smith/
        
        # Get the directory where the file was stored
        file_directory = os.path.dirname(file_path)
        
        # Check if the directory is within MEDIA_ROOT/timeoff_documents/
        # This prevents accidentally deleting directories outside our control
        media_timeoff_dir = os.path.join(settings.MEDIA_ROOT, 'timeoff_documents')
        
        if os.path.commonpath([media_timeoff_dir, file_directory]) == media_timeoff_dir:
            try:
                # Use os.listdir to check if empty, then os.rmdir for empty dirs
                # Or shutil.rmtree for non-empty dirs (be careful with this!)
                # For this specific case, we want to delete only if empty after file deletion.
                if not os.listdir(file_directory): # Check if directory is empty
                    os.rmdir(file_directory)
                    print(f"Deleted empty folder: {file_directory}") # For debugging
                else:
                    print(f"Folder {file_directory} not empty, skipping folder deletion.")
            except OSError as e:
                print(f"Error deleting folder {file_directory}: {e}")
        else:
            print(f"Directory {file_directory} is outside expected media path, skipping folder deletion.")