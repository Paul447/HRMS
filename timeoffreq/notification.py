from django.contrib.contenttypes.models import ContentType
from timeoffreq.services import  get_supervisor_for_user
import logging
from notificationapp.models import Notification

logger = logging.getLogger(__name__)

def notification_trigger(timeoff_request_instance):
    requester = timeoff_request_instance.employee
    supervisor_profile, supervisor_email = get_supervisor_for_user(requester)

    if supervisor_profile and supervisor_email:
            try:
                # Create in-app notification
                Notification.objects.create(
                    actor=requester,
                    recipient=supervisor_profile.user,
                    verb='Time Off request',
                    content_type=ContentType.objects.get_for_model(timeoff_request_instance),
                    object_id=timeoff_request_instance.id,
                    description=f"{requester.username} has created a Time Off request."
                )
                logger.info(f"In-app notification created for supervisor {supervisor_profile.user.username}.")

            except Exception as e:
                logger.error(f"FATAL ERROR during notification/email sending for PTO request ID {timeoff_request_instance.id}: {e}", exc_info=True)
    else:
            logger.warning(
                f"Notification and email for PTO request from {requester.username} (ID: {timeoff_request_instance.id}) "
                f"were skipped due to missing supervisor or supervisor email."
            )
   