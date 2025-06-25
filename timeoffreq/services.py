import logging
from department.models import UserProfile # Import UserProfile
from django.contrib.auth import get_user_model


User = get_user_model()
logger = logging.getLogger(__name__)

# Re-including send_custom_email and get_supervisor_for_user for completeness
# (These should ideally be in timeoffreq/services.py as per your imports)

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
    from django.conf import settings # Import settings locally or ensure it's available
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.core.mail import get_connection, EmailMultiAlternatives

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
    This supervisor is the manager of the user's department.

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
                f"Cannot find department manager."
            )
    except UserProfile.DoesNotExist:
        logger.error(
            f"UserProfile not found for user {user.username} (ID: {user.id})."
        )
    except Exception as e:
        logger.error(f"Error finding supervisor for user {user.username}: {e}", exc_info=True)

    return None, None

def check_is_user_manager_and_get_superuser_email(user):
    """
    Checks if the given user is marked as a manager in their UserProfile.
    If they are, it attempts to find and return the email of the first active superuser.

    Args:
        user (User): The user object to check.

    Returns:
        tuple: (bool, str or None).
               - True and the superuser's email if:
                 1. The user is authenticated.
                 2. The user has an associated UserProfile.
                 3. UserProfile.is_manager is True.
                 4. An active superuser is found.
               - False and None otherwise.
    """
    if not user.is_authenticated:
        return False, None

    try:
        user_profile = UserProfile.objects.get(user=user)

        if user_profile.is_manager:
            super_user_instance = User.objects.filter(is_superuser=True, is_active=True).first()
            
            if super_user_instance:
                return True, super_user_instance.email
            else:
                # User is a manager, but no active superuser was found.
                # Per requirements: "if not found fail silently" for superuser case.
                return False, None # This means a superuser email couldn't be retrieved
        else:
            # User has a profile but is not marked as a manager.
            return False, None
            
    except UserProfile.DoesNotExist:
        return False, None
    except Exception as e:
        logger.error(f"An unexpected error occurred in check_is_user_manager_and_get_superuser_email: {e}", exc_info=True)
        return False, None