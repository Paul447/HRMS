import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from department.models import UserProfile # Import UserProfile
from django.core.mail import get_connection, EmailMultiAlternatives

logger = logging.getLogger(__name__)
def send_custom_email(subject, recipient_list, template_name, context=None, html_email=True):
    """
    Sends an email using Django's EmailMultiAlternatives with a single SMTP connection.

    Args:
        subject (str): The subject of the email.
        recipient_list (list): A list of email addresses to send the email to.
        template_name (str): The path to the email template.
        context (dict, optional): Context variables for the template. Defaults to None.
        html_email (bool, optional): If True, sends HTML email. Defaults to True.

    Returns:
        int: The number of emails sent.
    """
    if not recipient_list:
        logger.warning("No recipient email addresses provided for subject: '%s'. Skipping email send.", subject)
        return 0

    if context is None:
        context = {}

    try:
        # Render template once
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message) if html_email else html_message

        # Use a single SMTP connection
        with get_connection(fail_silently=True) as connection:
            messages = []
            for recipient in recipient_list:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient],
                    connection=connection
                )
                if html_email:
                    msg.attach_alternative(html_message, "text/html")
                messages.append(msg)

            # Send all emails in one go
            num_sent = connection.send_messages(messages)
            if num_sent:
                logger.info("Email sent successfully to %s for subject: '%s'. Sent %s emails.",
                            ', '.join(recipient_list), subject, num_sent)
            else:
                logger.warning("No emails sent to %s for subject: '%s'. Possible SMTP issue.",
                               ', '.join(recipient_list), subject)
            return num_sent
    except (ValueError, AttributeError, TypeError) as e:
        logger.error("Error rendering template or preparing email for subject '%s': %s",
                     subject, e, exc_info=True)
        return 0
    except Exception as e:
        logger.error("Unexpected error sending email to %s for subject '%s': %s",
                     ', '.join(recipient_list), subject, e, exc_info=True)
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