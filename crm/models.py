from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Organization(models.Model):
    class CategoryBusiness(models.TextChoices):
        HOSPITAL = "Hospital", "Hospital"
        CLINIC = "Clinic", "Clinic"
        VENDOR = "Vendor", "Vendor"
        OTHER = "Other", "Other"

    business_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    suite = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    zipcode = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    ein = models.CharField(max_length=20, null=True, blank=True)
    category_business = models.CharField(
        max_length=20, choices=CategoryBusiness.choices, null=True, blank=True
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()  # Default manager

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.business_name

    @property
    def full_address(self):
        return ", ".join(
            filter(
                None,
                [
                    self.address,
                    self.suite,
                    self.city,
                    self.state,
                    self.zipcode,
                    self.country,
                ],
            )
        )


class Contact(models.Model):
    class ContactType(models.TextChoices):
        PRIMARY = "Primary", "Primary"
        SECONDARY = "Secondary", "Secondary"
        BILLING = "Billing", "Billing"
        SHIPPING = "Shipping", "Shipping"
        OTHER = "Other", "Other"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    title = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Opportunity(models.Model):
    class CategoryStage(models.TextChoices):
        POTENTIAL = "Potential", "Potential"
        QUALIFIED = "Qualified", "Qualified"
        WORKING = "Working", "Working"
        CLOSED = "Closed", "Closed"
        PENDING = "Pending", "Pending"
        LOST = "Lost", "Lost"

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="opportunities"
    )
    agent = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="opportunities"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    close_date = models.DateField()
    stage = models.CharField(max_length=20, choices=CategoryStage.choices)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.amount = round(self.amount, 2)
        super().save(*args, **kwargs)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return f"{self.organization.business_name} - {self.amount}"


class Note(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="notes"
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.note
