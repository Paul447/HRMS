from django.contrib.contenttypes.models import ContentType
from timeoffreq.services import get_supervisor_for_user, send_custom_email
from notificationapp.models import Notification
from department.models import UserProfile # Import UserProfile
from datetime import datetime
from timeoffreq.services import check_is_user_manager_and_get_superuser_email
from logging import getLogger

logger = getLogger(__name__)
def notification_and_email_trigger(timeoff_request_instance):
    """
    Triggers in-app notifications and emails based on the time-off request.
    - If requester is a normal user: notify their department manager.
    - If requester is a manager: notify the first active superuser.
    """
    requester = timeoff_request_instance.employee
    recipient_user_profile = None
    recipient_email = None
    email_subject = 'New Time Off Request Submitted'
    email_template = 'emails/timeoff_request_notification.html' # Default template

    # --- Determine Recipient based on Requester's Role ---
    try:
        requester_profile = UserProfile.objects.get(user=requester)

        if requester_profile.is_manager:
            # Requester is a manager, notify a superuser
            is_manager_result, superuser_email = check_is_user_manager_and_get_superuser_email(requester)
            if is_manager_result and superuser_email:
                # We don't have a specific UserProfile object for the superuser here,
                # just their email. For in-app notification, we'd need to fetch their UserProfile.
                # For this scenario, we might skip in-app notification if we can't easily get recipient_user_profile.
                # Or, if 'superuser_email' implies a specific superuser user, fetch their UserProfile.
                
                # For simplicity here, if superuser_email is found, use it for email,
                # and assume in-app notification for superusers is less critical or handled differently.
                # If an in-app notification for superusers is needed, you'd need to fetch the superuser's UserProfile.
                recipient_email = superuser_email
                email_subject = 'Manager Time Off Request Submitted (For Superuser Review)'
                logger.info(f"Requester {requester.username} is a manager. Will attempt to notify superuser: {recipient_email}")
                
                # Try to find the superuser's profile for in-app notification
                try:
                    recipient_user_profile = UserProfile.objects.get(user__email=superuser_email)
                except UserProfile.DoesNotExist:
                    logger.warning(f"Superuser profile not found for email {superuser_email}. In-app notification for superuser skipped.")
                    recipient_user_profile = None # Explicitly set to None if profile not found
            else:
                logger.warning(f"Requester {requester.username} is a manager, but no active superuser email found. Skipping email notification.")
                # Per requirement "if not found fail silently" -> so we just don't send the email here.
                return # Exit if manager but no superuser found/email.

        else:
            # Requester is a normal user, notify their department manager
            manager_profile, manager_email = get_supervisor_for_user(requester)
            if manager_profile and manager_email:
                recipient_user_profile = manager_profile
                recipient_email = manager_email
                logger.info(f"Requester {requester.username} is a normal user. Will notify manager: {recipient_email}")
            else:
                logger.warning(
                    f"Requester {requester.username} is a normal user, but no manager or manager email found for their department. Skipping notification."
                )
                return # Exit if normal user but no manager found/email.

    except UserProfile.DoesNotExist:
        logger.error(f"UserProfile not found for requester {requester.username} (ID: {requester.id}). Skipping notifications.")
        return
    except Exception as e:
        logger.error(f"FATAL ERROR determining recipient for PTO request ID {timeoff_request_instance.id}: {e}", exc_info=True)
        return


    # --- Send In-App Notification (if recipient_user_profile is available) ---
    if recipient_user_profile:
        try:
            Notification.objects.create(
                actor=requester,
                recipient=recipient_user_profile.user,
                verb='Time Off request',
                content_type=ContentType.objects.get_for_model(timeoff_request_instance),
                object_id=timeoff_request_instance.id,
                description=f"{requester.username} has created a Time Off request."
            )
            logger.info(f"In-app notification created for {recipient_user_profile.user.username}.")
        except Exception as e:
            logger.error(f"Error creating in-app notification for PTO request ID {timeoff_request_instance.id}: {e}", exc_info=True)
    else:
        logger.warning(f"In-app notification skipped for PTO request ID {timeoff_request_instance.id} due to missing recipient profile.")


    # --- Send Email Notification (if recipient_email is available) ---
    if recipient_email:
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
                'reason': timeoff_request_instance.employee_leave_reason or 'No reason provided',
                'current_year': datetime.now().year,
            }

            send_custom_email(
                subject=email_subject,
                recipient_list=[recipient_email],
                template_name=email_template,
                context=email_context,
                html_email=True
            )
        except Exception as e:
            logger.error(f"Error sending email for PTO request ID {timeoff_request_instance.id}: {e}", exc_info=True)
    else:
        logger.warning(f"Email notification skipped for PTO request ID {timeoff_request_instance.id} due to missing recipient email.")