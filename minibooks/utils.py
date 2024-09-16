from django.db import models
from .models import *
from django.db.models import Q
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


def log_uploadhistory(user, action, result, uploadhistory):
    """
    Logs an upload history action for a user.

    Args:
        user (User): The user performing the action.
        action (str): The action performed by the user.
        result (str): The result of the action.
        uploadhistory (UploadHistory): The upload history record associated with the action.

    Returns:
        None
    """
    UploadHistoryTrack.objects.create(
        user=user, action=action, result=result, uploadhistory=uploadhistory
    )
