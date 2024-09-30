from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from customer.models import Company
from django.core.validators import MinValueValidator, MaxValueValidator
from utils.base_func import get_specialty_choices


class CustomUser(AbstractUser):
    # Admin or not
    is_admin = models.BooleanField("Is admin", default=False)
    # doctor or not
    is_doctor = models.BooleanField("Is Provider", default=False)
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
    # SPECIALTY_CHOICES = {
    #     "복부비뇨": "복부/비뇨생식기",
    #     "신경두경": "신경두경부",
    #     "흉부심장": "흉부심장",
    #     "심잘혈관": "심장혈관",
    #     "근골격": "근골격",
    #     "유방갑상": "유방/갑상선",
    #     "소아": "소아",
    #     "인터벤션": "인터벤션",
    #     "정형외과": "정형외과",
    # }
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
    extra_info2_int = models.IntegerField(null=True, blank=True, default=0)
    extra_info3_bool = models.BooleanField("Extra info 3", default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
