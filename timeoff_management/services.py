# import logging
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from notificationapp.models import Notification
# from django.contrib.auth import get_user_model
# from HRMS.settings import COMPANY_NAME


# logger = logging.getLogger(__name__)
# User = get_user_model()


# def send_pto_notification_and_email(time_off_instance, reviewer, new_status):
#     """
#     Sends a notification and an email to the user whose PTO request
#     has been updated (approved or rejected).

#     Args:
#         time_off_instance: The time off Requests instance that was updated.
#         reviewer: The user who performed the action (approver/rejecter).
#         new_status: The new status of the PTO request ('approved' or 'rejected').
#     """
#     recipient = time_off_instance.employee
#     start_date_time = time_off_instance.start_date_time
#     time_off_hours = time_off_instance.time_off_duration
#     subject = ""
#     notification_description = ""
#     email_template_name = ""
#     level = ""

#     if new_status == "approved":
#         subject = f"Your PTO Request for {start_date_time} Has Been Approved!"
#         notification_description = f"Your PTO request for {start_date_time} has been approved."
#         email_template_name = "emails/pto_approved_email.html"
#         level = "success"
#         logger.info(f"PTO request approved by {reviewer.username} for user {recipient.username}.")
#     elif new_status == "rejected":
#         subject = f"Your PTO Request for {start_date_time} Has Been Rejected."
#         notification_description = f"Your PTO request for {start_date_time} has been rejected."
#         email_template_name = "emails/pto_rejected_email.html"
#         level = "error"
#         logger.info(f"PTO request rejected by {reviewer.username} for user {recipient.username}.")
#     else:
#         logger.warning(f"Attempted to send notification/email for unknown PTO status: {new_status}")
#         return

#     # Create a notification
#     try:
#         Notification.objects.create(actor=reviewer, recipient=recipient, verb=new_status, description=notification_description, level=level, content_object=time_off_instance)
#         logger.debug(f"Notification created for {recipient.username} (status: {new_status}).")
#     except Exception as e:
#         logger.error(f"Error creating notification for PTO request {time_off_instance.id}: {e}")

#     # Send an email
#     try:
#         context = {
#             "user_name": recipient.first_name,
#             "start_date": start_date_time,
#             "end_date": time_off_instance.end_date_time,
#             "reason": time_off_instance.employee_leave_reason,
#             "status": new_status.capitalize(),
#             "approved_by": reviewer.first_name,
#             "time_off": time_off_hours,
#             "site_name": COMPANY_NAME,
#             # 'site_url': 'https://yourcompany.com', # Replace with your actual site URL
#         }
#         html_message = render_to_string(email_template_name, context)
#         plain_message = f"Dear {recipient.first_name},\n\nYour PTO request from {start_date_time} to {time_off_instance.end_date_time} has been {new_status}.\n\nReason: {time_off_instance.employee_leave_reason}\n\nRegards,\nYour Company Name"

#         send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [recipient.email], html_message=html_message, fail_silently=False)
#         logger.info(f"Email sent to {recipient.email} for PTO request {time_off_instance.id} (status: {new_status}).")
#     except Exception as e:
#         logger.error(f"Error sending email for PTO request {time_off_instance.id} to {recipient.email}: {e}")
