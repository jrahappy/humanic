from django.contrib import admin
from .models import ChoiceMaster


class ChoiceMasterAdmin(admin.ModelAdmin):
    list_display = ("choice_name", "choice_key", "choice_value", "choice_order")
    ordering = ("choice_name", "choice_order")
    search_fields = ("choice_name", "choice_value")


admin.site.register(ChoiceMaster, ChoiceMasterAdmin)
