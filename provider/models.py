# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Provider(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    doctor_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name
