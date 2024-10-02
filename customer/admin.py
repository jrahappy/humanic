from django.contrib import admin
from .models import Company, ServiceFee, Contract


# class CompanyAdmin(admin.ModelAdmin):
#     list_display = [
#         "business_name",
#         "is_public",
#         "president_name",
#         "address",
#         "suite",
#         "city",
#         "state",
#         "country",
#         "zipcode",
#         "office_phone",
#         "office_fax",
#         "office_email",
#         "website",
#     ]
#     search_fields = ["business_name", "president_name"]


# admin.site.register(Company, CompanyAdmin)


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 1


class CompanyAdmin(admin.ModelAdmin):
    inlines = [ContractInline]
    list_display = [
        "business_name",
        "is_clinic",
        "address",
        "suite",
        "city",
        "office_email",
    ]
    search_fields = ["business_name", "president_name"]
    list_filter = ["is_clinic"]


admin.site.register(Company, CompanyAdmin)


class ServiceFeeAdmin(admin.ModelAdmin):
    list_display = ["company", "name", "category", "rate", "rule", "is_active"]
    search_fields = ["company", "name"]
    list_filter = ["category", "is_active"]
    list_editable = ["is_active"]
    list_per_page = 10


admin.site.register(ServiceFee, ServiceFeeAdmin)
