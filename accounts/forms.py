from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm, LoginForm, ChangePasswordForm
from allauth.account.views import PasswordChangeView
from django import forms
from .models import *
from accounts.models import CustomUser, Profile


class CustomPasswordChangeForm(ChangePasswordForm):
    oldpassword = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Old Password"}),
    )
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"placeholder": "New Password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
    )

    class Meta:
        model = CustomUser
        fields = ("oldpassword", "password1", "password2")

    def save(self, request):
        user = request.user
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "user",
            "avatar",
            "license_number",
            "real_name",
            "email",
            "cellphone",
            "specialty2",
            "specialty3",
            "specialty4",
            "specialty5",
            "bio",
        ]
        widgets = {
            "user": forms.HiddenInput(),
        }
