from django.db import models
from taggit.managers import TaggableManager


# Create your models here.
class Company(models.Model):
    customuser = models.ForeignKey(
        "accounts.CustomUser", null=True, blank=True, on_delete=models.SET_NULL
    )
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
    #  협진병원 여부
    is_collab = models.BooleanField(default=False, null=True, blank=True)
    # taggit
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.business_name

    @property
    def full_address(self):
        address_parts = [
            self.city or "",
            self.state or "",
            self.address or "",
            self.suite or "",
            self.zipcode or "",
            self.country or "",
        ]
        return " ".join(part for part in address_parts if part).strip(" ")


class ServiceFee(models.Model):
    Fee_Type = [
        ("P", "Percent"),
        ("F", "Flat Fee"),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    service_company = models.ForeignKey(
        Company,
        on_delete=models.DO_NOTHING,
        related_name="service_company",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=1, choices=Fee_Type, default="P")
    rate = models.DecimalField(decimal_places=3, max_digits=5)
    rule = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        service_company_name = (
            self.service_company.business_name
            if self.service_company
            else "No Service Company"
        )
        return service_company_name + " - " + self.name


class Contract(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    service_fee = models.ForeignKey(ServiceFee, on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(default=False)


class CustomerLog(models.Model):
    LOG_LEVEL = [
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LOG_LEVEL, default="INFO")
    log = models.TextField()
    updated_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.DO_NOTHING, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            self.company.business_name
            + " - "
            + self.level
            + " - "
            + self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )


class CustomerContact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    office_phone = models.CharField(max_length=20, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def upload_customer_files_location(instance, filename):
    return f"customerfiles/{instance.company.id}/{filename}"


class CustomerFiles(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    file_name = models.CharField(max_length=250, null=True, blank=True)
    file = models.FileField(
        upload_to=upload_customer_files_location, max_length=250, null=True, blank=True
    )

    def __str__(self):
        return self.user.username + " " + self.name
