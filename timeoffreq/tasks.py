import logging

logger = logging.getLogger(__name__)

def trigger_notification_and_email_task(self, request_id):
    from .models import TimeoffRequest
    from .notification import notification_and_email_trigger
    try:
        request_instance = TimeoffRequest.objects.select_related(
            "employee", "requested_leave_type__leave_type"
        ).get(pk=request_id)
        notification_and_email_trigger(request_instance)
    except TimeoffRequest.DoesNotExist:
        logger.error(f"TimeoffRequest with id {request_id} does not exist.")

