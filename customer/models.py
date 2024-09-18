from django.db import models


# Create your models here.
class Company(models.Model):
    business_name = models.CharField(max_length=100, null=True, blank=True)
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
    clinic_id = models.CharField(max_length=20, null=True, blank=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.business_name


class Contract(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contract_name = models.CharField(max_length=100, null=True, blank=True)
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    contract_description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"

    def __str__(self):
        return self.contract_name


class ContractItem(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    item_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Contract Item"
        verbose_name_plural = "Contract Items"

    def __str__(self):
        return self.product.product_name


class Product(models.Model):
    product_name = models.CharField(max_length=100, null=True, blank=True)
    bodypart = models.CharField(max_length=50, null=True, blank=True)
    modality = models.CharField(max_length=50, null=True, blank=True)
    equipment = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    emergency = models.BooleanField(default=False)
    onsite = models.BooleanField(default=False)
    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.product_name


class Platform(models.Model):
    platform_name = models.CharField(max_length=100, null=True, blank=True)
    platform_description = models.TextField(null=True, blank=True)
    platform_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"

    def __str__(self):
        return self.platform_name
