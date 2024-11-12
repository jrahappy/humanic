from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm, ChangePasswordForm
from django import forms
from .models import *
from accounts.models import CustomUser, Profile
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


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


class CustomSignupForm(SignupForm):

    username = forms.CharField(max_length=30, label="Username")
    email = forms.EmailField(label="Email")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    is_doctor = forms.BooleanField(label="I am a doctor", required=False)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.is_doctor = self.cleaned_data.get("is_doctor")
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


class HRFilesForm(forms.ModelForm):
    class Meta:
        model = HRFiles
        fields = ["file"]
        # widgets = {
        #     "user": forms.HiddenInput(),
        # }
