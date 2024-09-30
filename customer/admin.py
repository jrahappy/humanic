from django.contrib import admin
from .models import Company, Contract


class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "business_name",
        "is_public",
        "president_name",
        "address",
        "suite",
        "city",
        "state",
        "country",
        "zipcode",
        "office_phone",
        "office_fax",
        "office_email",
        "website",
    ]
    search_fields = ["business_name", "president_name"]


admin.site.register(Company, CompanyAdmin)


class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "company",
        "contract_name",
        "contract_start",
        "contract_end",
        "contract_description",
    ]


admin.site.register(Contract, ContractAdmin)
