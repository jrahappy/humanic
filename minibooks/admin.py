from django.contrib import admin
from .models import ReportMaster, UploadHistory


class ReportMasterAdmin(admin.ModelAdmin):
    list_display = [
        "apptitle",
        "radiologist",
    ]
    search_fields = ["apptitle", "radiologist"]


admin.site.register(ReportMaster, ReportMasterAdmin)
admin.site.register(UploadHistory)
