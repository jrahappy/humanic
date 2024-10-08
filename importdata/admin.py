from django.contrib import admin
from .models import (
    rawdata,
    importhistory,
    temp_doctor_table,
    temp_customer_table,
    cleanData,
)
from import_export.admin import ImportExportModelAdmin
