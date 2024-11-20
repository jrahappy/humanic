from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.base_func import (
    get_specialty_choices,
    get_amodality_choices,
    APPT_DAYS,
    HOLIDAY_CATEGORY,
    TERM_CATEGORY,
    CONTRACT_STATUS,
)
from customer.models import Company


class CustomUser(AbstractUser):
    # Admin or not
    is_admin = models.BooleanField("Is admin", default=False)
    # doctor or not
    is_doctor = models.BooleanField("Is Doctor", default=False)
    # CBCT/False, SAVVY/True
    is_terms = models.BooleanField("Is Terms", default=False)
    is_privacy = models.BooleanField("Is Privacy", default=False)
    is_staff = models.BooleanField("Is Staff", default=False)
    is_superuser = models.BooleanField("Is Superuser", default=False)
    is_active = models.BooleanField("Is Active", default=True)

    def __str__(self):
        return self.username

    def clean(self):
        # Check if a user with the same username already exists
        if (
            CustomUser.objects.filter(username=self.username)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("Username already exists.")

        # Check if a user with the same email already exists
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists.")

        super().clean()

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    real_name = models.CharField(max_length=30, null=True, blank=True)
    specialty1 = models.CharField(max_length=30, null=True, blank=True)
    specialty2 = models.CharField(
        max_length=30, choices=get_specialty_choices, null=True, blank=True
    )
    specialty3 = models.CharField(
        max_length=30, choices=get_specialty_choices, null=True, blank=True
    )
    specialty4 = models.CharField(
        max_length=30, choices=get_specialty_choices, null=True, blank=True
    )
    specialty5 = models.CharField(
        max_length=30, choices=get_specialty_choices, null=True, blank=True
    )
    position = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cv3_id = models.CharField(max_length=30, null=True, blank=True)
    onpacs_id = models.CharField(max_length=30, null=True, blank=True)

    bio = models.TextField(null=True, blank=True)
    cellphone = models.CharField(max_length=30, null=True, blank=True)
    # company = models.ForeignKey(
    #     Company, on_delete=models.CASCADE, null=True, blank=True
    # )
    employee_id = models.CharField(max_length=30, null=True, blank=True)
    fee_rate = models.FloatField(
        null=True,
        blank=True,
        default=0.7,
        help_text="0.0~1.0",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    license_number = models.CharField(max_length=20, null=True, blank=True)
    contract_status = models.CharField(
        max_length=1, choices=CONTRACT_STATUS, default="A"
    )
    extra_info2_int = models.IntegerField(null=True, blank=True, default=0)
    extra_info3_bool = models.BooleanField("Extra info 3", default=False)

    def __str__(self):
        return self.real_name

    def save(self, *args, **kwargs):
        if self.real_name:
            self.real_name = self.real_name.strip()
        CustomUser.objects.filter(pk=self.user.pk).update(
            first_name=self.real_name, email=self.email
        )
        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class WorkHours(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    work_weekday = models.CharField(
        choices=APPT_DAYS, max_length=1, null=True, blank=True
    )
    # work_hour = models.CharField(max_length=250, null=True, blank=True)
    work_hour = models.JSONField(default=list)

    def __str__(self):
        return self.work_weekday


class Holidays(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    holiday_category = models.CharField(choices=HOLIDAY_CATEGORY, max_length=1)
    holiday_name = models.CharField(max_length=30)
    holidays = models.JSONField(default=list)
    holiday_date_from = models.DateField(null=True, blank=True)
    holiday_date_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.holiday_name


class ProductionTarget(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    work_weekday = models.CharField(choices=APPT_DAYS, max_length=1, default="1")
    modality = models.CharField(choices=get_amodality_choices, max_length=10)
    target_value = models.SmallIntegerField(default=0)
    max_value = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.term_category + " " + self.modality + " " + self.target_value


def upload_location(instance, filename):
    return f"hrfiles/{instance.user.username}/{filename}"


class HRFiles(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=50, null=True, blank=True)
    file_name = models.CharField(max_length=250, null=True, blank=True)
    file = models.FileField(
        upload_to=upload_location, max_length=250, null=True, blank=True
    )

    def __str__(self):
        return self.user.username + " " + self.name
