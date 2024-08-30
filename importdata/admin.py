from django.contrib import admin
from .models import rawdata, importhistory
from import_export.admin import ImportExportModelAdmin


class rawdataAdmin(ImportExportModelAdmin):
    list_display = (
        "case_id",
        "name",
        "department",
        "bodypart",
        "modality",
        "equipment",
        "studydescription",
        "imagecount",
        "accessionnumber",
        "readprice",
        "reader",
        "approver",
        "radiologist",
        "studydate",
        "approveddttm",
        "stat",
        "pacs",
        "requestdttm",
        "ecode",
        "sid",
        "patientid",
        "created_at",
        "updated_at",
    )


admin.site.register(rawdata, rawdataAdmin)
admin.site.register(importhistory)
