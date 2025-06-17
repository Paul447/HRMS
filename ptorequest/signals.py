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