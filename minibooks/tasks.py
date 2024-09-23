from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ReportMaster, UploadHistory


@shared_task
def upload_file(file_name, file_content):
    path = default_storage.save(file_name, ContentFile(file_content))
    return path


@shared_task(bind=True)
def update_is_onsite(self, row_id, is_onsite):
    is_onsite = True if is_onsite == "True" else False
    rm = ReportMaster.objects.get(id=row_id)
    rm.is_onsite = is_onsite
    rm.save()
    # print(f"Updated is_onsite for row_id: {row_id} to {is_onsite}")

    return "Done"
