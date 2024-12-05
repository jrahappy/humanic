from django.contrib import admin
from .models import Company, ServiceFee, Contract


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    inlines = [ContractInline]
    list_display = [
        "business_name",
        "is_clinic",
        "city",
        "office_email",
        "tag_list",
    ]
    search_fields = ["business_name"]
    list_filter = ["is_clinic", "is_collab"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())


admin.site.register(Company, CompanyAdmin)


class ServiceFeeAdmin(admin.ModelAdmin):
    list_display = ["company", "name", "category", "rate", "rule", "is_active"]
    search_fields = ["company", "name"]
    list_filter = ["category", "is_active"]
    list_editable = ["is_active"]
    list_per_page = 10


admin.site.register(ServiceFee, ServiceFeeAdmin)
