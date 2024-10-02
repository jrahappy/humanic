from django.db import models
from product.models import Product, Platform


# Create your models here.
class Company(models.Model):
    business_name = models.CharField(max_length=100)
    president_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    suite = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    office_phone = models.CharField(max_length=20, null=True, blank=True)
    office_fax = models.CharField(max_length=20, null=True, blank=True)
    office_email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    ein = models.CharField(max_length=20, null=True, blank=True)
    contact_person = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    is_clinic = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.business_name

    @property
    def full_address(self):
        address_parts = [
            self.address or "",
            self.suite or "",
            self.city or "",
            self.state or "",
            self.zipcode or "",
            self.country or "",
        ]
        return ", ".join(part for part in address_parts if part).strip(", ")


class ServiceFee(models.Model):
    Fee_Type = [
        ("P", "Percent"),
        ("F", "Flat Fee"),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=1, choices=Fee_Type, default="P")
    rate = models.DecimalField(decimal_places=3, max_digits=5)
    rule = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company.business_name + " - " + self.name


class Contract(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    service_fee = models.ForeignKey(ServiceFee, on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(default=False)
