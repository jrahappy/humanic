from django.contrib import admin
from .models import Company, Contract, ContractItem, Product, Platform


class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        "business_name",
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


class ContractItemAdmin(admin.ModelAdmin):
    list_display = ["contract", "product", "item_price"]


admin.site.register(ContractItem, ContractItemAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "product_name",
        "bodypart",
        "modality",
        "equipment",
        "description",
        "emergency",
        "onsite",
        "product_price",
    ]


admin.site.register(Product, ProductAdmin)

admin.site.register(Platform)
