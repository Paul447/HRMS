import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from department.models import UserProfile # Import UserProfile

logger = logging.getLogger(__name__)

def send_custom_email(subject, recipient_list, template_name, context=None, html_email=True):
    """
    Sends an email using Django's send_mail function, rendering a template.

    Args:
        subject (str): The subject of the email.
        recipient_list (list): A list of email addresses to send the email to.
        template_name (str): The path to the email template (e.g., 'emails/pto_request_notification.html').
        context (dict, optional): A dictionary of context variables to pass to the template. Defaults to None.
        html_email (bool, optional): If True, renders HTML from the template.
                                      If False, renders plain text. Defaults to True.
    Returns:
        int: The number of emails sent.
    """
    if not recipient_list:
        logger.warning(f"No recipient email addresses provided for subject: '{subject}'. Skipping email send.")
        return 0

    if context is None:
        context = {}

    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message) if html_email else html_message

        num_sent = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message if html_email else None,
            fail_silently=False, # Set to True in production if you want to suppress errors
        )
        logger.info(f"✅ Email sent successfully to {', '.join(recipient_list)} for subject: '{subject}'. Sent {num_sent} emails.")
        return num_sent
    except Exception as e:
        logger.error(f"❌ Error sending email to {', '.join(recipient_list)} for subject '{subject}': {e}", exc_info=True)
        return 0

def get_supervisor_for_user(user):
    """
    Finds and returns the supervisor UserProfile and their email for a given user.

    Args:
        user (User): The user for whom to find the supervisor.

    Returns:
        tuple: (supervisor_user_profile, supervisor_email) or (None, None) if not found.
    """
    try:
        requester_profile = UserProfile.objects.get(user=user)
        department = requester_profile.department
        if department:
            supervisor_to_notify = UserProfile.objects.filter(
                department=department,
                is_manager=True
            ).first()

            if supervisor_to_notify and supervisor_to_notify.user:
                return supervisor_to_notify, supervisor_to_notify.user.email
            else:
                logger.warning(
                    f"No manager found in department '{department.name}' "
                    f"for user {user.username} (ID: {user.id})."
                )
        else:
            logger.warning(
                f"User {user.username} (ID: {user.id}) has no department. "
                f"Cannot find supervisor."
            )
    except UserProfile.DoesNotExist:
        logger.error(
            f"UserProfile not found for user {user.username} (ID: {user.id})."
        )
    except Exception as e:
        logger.error(f"Error finding supervisor for user {user.username}: {e}", exc_info=True)

    return None, None