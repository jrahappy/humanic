from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, WorkHours, Holidays, ProductionTarget
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "username",
        "email",
        "first_name",
        "is_staff",
        "is_doctor",
        "is_active",
        "date_joined",
    ]
    search_fields = ["email", "username", "first_name", "last_name"]
    list_filter = ["last_login", "is_doctor", "date_joined"]
    ordering = ["-username"]

    # Add fieldsets to show 'is_doctor' in the user change form
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("email", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_doctor",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields to display when adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_doctor",
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = [
        "user",
        "real_name",
        "email",
        "specialty1",
        "specialty2",
        "fee_rate",
    ]
    search_fields = ["real_name"]


admin.site.register(Profile, ProfileAdmin)

admin.site.register(WorkHours)
admin.site.register(Holidays)
admin.site.register(ProductionTarget)
