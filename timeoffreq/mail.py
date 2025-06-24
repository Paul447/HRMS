from django.contrib.contenttypes.models import ContentType
from timeoffreq.services import  get_supervisor_for_user , send_custom_email
import logging
from notificationapp.models import Notification

logger = logging.getLogger(__name__)

def mail_trigger(timeoff_request_instance):
    requester = timeoff_request_instance.employee
    supervisor_profile, supervisor_email = get_supervisor_for_user(requester)

    if supervisor_profile and supervisor_email:
            try:
                # Create mail notification
                # Prepare email context
                email_context = {
                    'requester_name': requester.get_full_name(),
                    'leave_type': timeoff_request_instance.requested_leave_type.leave_type.name if timeoff_request_instance.requested_leave_type else 'N/A',
                    'start_date': timeoff_request_instance.start_date_time if timeoff_request_instance.start_date_time else 'N/A',
                    'end_date': timeoff_request_instance.end_date_time if timeoff_request_instance.end_date_time else 'N/A',
                    'total_hours': timeoff_request_instance.time_off_duration if timeoff_request_instance.time_off_duration else 0,
                    'reason': timeoff_request_instance.employee_leave_reason if timeoff_request_instance.employee_leave_reason else 'N/A',
                }

                # Send email
                send_custom_email(
                    subject='New PTO Request Submitted',
                    recipient_list=[supervisor_email],
                    template_name='emails/pto_request_notification.html', # Create this template
                    context=email_context,
                    html_email=True
                )


            except Exception as e:
                logger.error(f"FATAL ERROR during notification/email sending for PTO request ID {timeoff_request_instance.id}: {e}", exc_info=True)
    else:
            logger.warning(
                f"Notification and email for PTO request from {requester.username} (ID: {timeoff_request_instance.id}) "
                f"were skipped due to missing supervisor or supervisor email."
            )
   