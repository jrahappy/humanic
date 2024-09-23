from django.db import models


class Product(models.Model):
    MODALITIES = {
        "CT": "CT",
        "MR": "MR",
        "CR": "CR",
        "MG": "MG",
        "US": "US",
    }
    name = models.CharField(max_length=100)
    product_code = models.CharField(max_length=20, blank=True, null=True)
    modality = models.CharField(max_length=2, choices=MODALITIES.items())
    emergency = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Platform(models.Model):
    name = models.CharField(max_length=20)
    fee_rate = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def __str__(self):
        return self.name
