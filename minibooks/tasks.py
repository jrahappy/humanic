from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ReportMaster, UploadHistory


@shared_task
def upload_file(file_name, file_content):
    path = default_storage.save(file_name, ContentFile(file_content))
    return path


@shared_task
def my_task(arg1, arg2):
    # Task logic here
    result = arg1 + arg2
    print(result)
    return result
