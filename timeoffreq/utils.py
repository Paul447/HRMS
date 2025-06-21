import os
import uuid
import datetime
# No need to import Django models (User, Department, LeaveType) directly here
# as they will be passed as instances or accessed via instance attributes.
# However, for type hinting or if you need get_user_model(), you can import it.
from django.contrib.auth import get_user_model # Still useful if you need the User model itself

# Optional: You might explicitly get the User model if needed elsewhere in this file,
# but for the upload path functions, `instance.user` is sufficient.
# User = get_user_model()


def _get_user_folder_name(user):
    """Generates a clean folder name for the user based on first-lastname."""
    first_name = user.first_name or "unknown"
    last_name = user.last_name or "user"
    return f"{first_name.replace(' ', '_').lower()}-{last_name.replace(' ', '_').lower()}"

def _get_leave_type_slug(leave_type_instance):
    """Generates a slug from the leave type name."""
    if leave_type_instance and hasattr(leave_type_instance, 'name'):
        return leave_type_instance.name.replace(' ', '_').lower()
    return "unspecified"

def _get_creation_datetime_string(created_at_datetime):
    """Generates a formatted datetime string for the filename."""
    if created_at_datetime:
        # Use UTC time to avoid timezone issues on different servers
        return created_at_datetime.astimezone(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')
    # Fallback to current UTC time if created_at isn't set (unlikely with auto_now_add)
    # Using current UTC time as a fallback for 2025-06-20 12:02:47 PM CDT is 2025-06-20 05:02:47 PM UTC
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')

def _generate_unique_id():
    """Generates a short, unique identifier."""
    return uuid.uuid4().hex[:8] # Using first 8 chars of hex UUID

def pto_document_upload_path(instance, filename):
    """
    Constructs the upload path for medical documents with a descriptive and unique filename.
    This function is intended to be used as the `upload_to` callable for a FileField.
    Files will be stored in:
    MEDIA_ROOT/timeoff_documents/<user_first_name>-<user_last_name>/<leave_type>-<created_date_time>-<unique_id>.<ext>
    """
    # Base directory for all PTO documents
    base_dir = 'timeoff_documents'

    # 1. Get the user's specific folder name
    # We directly access instance.user, assuming it's populated.
    # The `user` object passed to `_get_user_folder_name` is the `User` instance.
    user_folder = _get_user_folder_name(instance.user)

    # 2. Get the leave type slug
    # The `leave_type_instance` passed to `_get_leave_type_slug` is the `LeaveType` instance.
    leave_type_slug = _get_leave_type_slug(instance.leave_type)

    # 3. Get the formatted creation datetime string
    # The `created_at_datetime` passed to `_get_creation_datetime_string` is the datetime object.
    created_datetime_str = _get_creation_datetime_string(instance.created_at)

    # 4. Generate a unique ID for the filename
    unique_id = _generate_unique_id()

    # 5. Extract the original file extension
    ext = filename.split('.')[-1]

    # Construct the descriptive filename parts
    descriptive_filename_parts = [
        leave_type_slug,
        created_datetime_str,
        unique_id
    ]

    # Filter out any empty parts before joining
    clean_descriptive_parts = [part for part in descriptive_filename_parts if part]

    # Join the parts with hyphens to form the new filename, then add extension
    new_filename = f"{'-'.join(clean_descriptive_parts)}.{ext}"

    # Combine all parts to form the full upload path
    return os.path.join(base_dir, user_folder, new_filename)