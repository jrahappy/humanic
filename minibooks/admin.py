from django.contrib import admin
from .models import ReportMaster, UploadHistory, ReportMasterStat


class ReportMasterAdmin(admin.ModelAdmin):
    list_display = [
        "apptitle",
        "radiologist",
    ]
    search_fields = ["apptitle", "radiologist"]


admin.site.register(ReportMaster, ReportMasterAdmin)


class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_at",
    ]
    search_fields = ["name", "created_at"]


admin.site.register(UploadHistory, UploadHistoryAdmin)


class ReportMasterStatAdmin(admin.ModelAdmin):
    list_display = [
        "apptitle",
        "radiologist",
    ]
    search_fields = ["apptitle", "radiologist"]


admin.site.register(ReportMasterStat)
