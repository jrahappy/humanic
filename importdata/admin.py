from django.contrib import admin
from .models import (
    rawdata,
    importhistory,
    temp_doctor_table,
    temp_customer_table,
    cleanData,
)
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


class temp_doctor_tableAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "specialty",
        "doctor_id",
        "email",
        "cv3_id",
        "onpacs_id",
        "department",
        "position",
        "fee_rate",
    )


admin.site.register(temp_doctor_table, temp_doctor_tableAdmin)


class temp_customer_tableAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "customer_id",
    )


admin.site.register(temp_customer_table, temp_customer_tableAdmin)

admin.site.register(cleanData)
