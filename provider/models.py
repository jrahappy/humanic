# Create your models here.
from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    doctor_id = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=20, null=True, blank=True)
    cv3_id = models.CharField(max_length=20, null=True, blank=True)
    onpacs_id = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    fee_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return self.name
