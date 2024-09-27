from django.contrib import admin
from .models import (
    ReportMaster,
    UploadHistory,
    ReportMasterStat,
    MagamMaster,
    MagamDetail,
    HumanRules,
)


class ReportMasterAdmin(admin.ModelAdmin):
    list_display = [
        "apptitle",
        "radiologist",
    ]
    search_fields = ["apptitle", "radiologist"]


admin.site.register(ReportMaster, ReportMasterAdmin)


class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "platform",
        "imported",
        "verified",
        "aggregated",
        "is_deleted",
        "created_at",
    ]
    search_fields = ["name", "platform"]


admin.site.register(UploadHistory, UploadHistoryAdmin)


class ReportMasterStatAdmin(admin.ModelAdmin):
    list_display = [
        "apptitle",
        "radiologist",
    ]
    search_fields = ["apptitle", "radiologist"]


admin.site.register(ReportMasterStat)

admin.site.register(MagamMaster)


class HumanRulesAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "def_name",
        "def_value",
        "rules_order",
        "created_at",
    ]
    search_fields = [
        "name",
    ]
    ordering = ["rules_order"]


admin.site.register(HumanRules, HumanRulesAdmin)
