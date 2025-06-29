
import logging

from celery import shared_task
from .utils import update_experience_records

logger = logging.getLogger(__name__)


@shared_task
def update_experience_and_pto_task():
    return update_experience_records()
    