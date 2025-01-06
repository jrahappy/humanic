from django.contrib import admin
from .models import Refers, IllnessCode, TreatmentCode, SimpleDiagnosis, ReferHistory

# Register your models here.
admin.site.register(IllnessCode)
admin.site.register(TreatmentCode)
admin.site.register(Refers)


class ReferHistoryAdmin(admin.ModelAdmin):
    list_display = ["refer", "changed_status", "memo", "changed_at", "changed_by"]


admin.site.register(ReferHistory, ReferHistoryAdmin)


class SimpleDiagnosisAdmin(admin.ModelAdmin):
    list_display = ["code1", "code2", "code3", "code4", "order", "step", "is_head"]


admin.site.register(SimpleDiagnosis, SimpleDiagnosisAdmin)
