from django.contrib import admin
from .models import Product, Platform


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product_code",
        "modality",
        "emergency",
        "price",
    )  # Add the desired fields here


admin.site.register(Product, ProductAdmin)


class PlatformAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "fee_rate",
    )  # Add the desired fields here


admin.site.register(Platform, PlatformAdmin)
