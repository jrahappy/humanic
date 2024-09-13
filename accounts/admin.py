from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "is_staff", "is_doctor"]
    search_fields = ["email", "username"]
    ordering = ["-username"]


admin.site.register(CustomUser, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = [
        "user",
        "company",
        "real_name",
        "email",
        "specialty1",
        "specialty2",
        "fee_rate",
    ]
    search_fields = ["real_name"]


admin.site.register(Profile, ProfileAdmin)
