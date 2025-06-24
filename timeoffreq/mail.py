from django.contrib.contenttypes.models import ContentType
from timeoffreq.services import  get_supervisor_for_user , send_custom_email
import logging
from notificationapp.models import Notification
from django.utils import timezone

logger = logging.getLogger(__name__)

from datetime import datetime

def mail_trigger(timeoff_request_instance):
    requester = timeoff_request_instance.employee
    supervisor_profile, supervisor_email = get_supervisor_for_user(requester)

    if not supervisor_profile or not supervisor_email:
        logger.warning(
            "Notification and email for PTO request from %s (ID: %s) skipped due to missing supervisor or email.",
            requester.username, timeoff_request_instance.id
        )
        return

    try:
        email_context = {
            'requester_name': requester.get_full_name() or requester.username,
            'leave_type': (
                timeoff_request_instance.requested_leave_type.leave_type.name
                if timeoff_request_instance.requested_leave_type
                else 'N/A'
            ),
            'start_date': (
                timeoff_request_instance.start_date_time
                if timeoff_request_instance.start_date_time
                else 'N/A'
            ),
            'end_date': (
                timeoff_request_instance.end_date_time
                if timeoff_request_instance.end_date_time
                else 'N/A'
            ),
            'total_hours': timeoff_request_instance.time_off_duration or 0,
            'reason': timeoff_request_instance.employee_leave_reason or 'N/A',
            'current_year': datetime.now().year,  # Add current year
        }

        send_custom_email(
            subject='New PTO Request Submitted',
            recipient_list=[supervisor_email],
            template_name='emails/pto_request_notification.html',
            context=email_context,
            html_email=True
        )
    except (ValueError, AttributeError) as e:
        logger.error(
            "Error preparing email for PTO request ID %s: %s",
            timeoff_request_instance.id, e, exc_info=True
        )