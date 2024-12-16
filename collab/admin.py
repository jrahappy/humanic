from django.contrib import admin
from .models import Refers, IllnessCode, TreatmentCode

# Register your models here.
admin.site.register(IllnessCode)
admin.site.register(TreatmentCode)
