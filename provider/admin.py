from django.contrib import admin
from .models import Provider


class ProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "doctor_id", "department", "position"]
    search_fields = ["name", "email", "phone", "doctor_id", "department", "position"]

    class Meta:
        model = Provider


admin.site.register(Provider, ProviderAdmin)
