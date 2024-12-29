from django import forms
from .models import UploadHistory, MagamMaster
from utils.base_func import get_platform_choices
from allauth.account.forms import SignupForm, ChangePasswordForm


class CollabUserSignupForm(SignupForm):
    # username = forms.CharField(max_length=30, label="Username")
    # email = forms.EmailField(label="Email")
    # is_doctor = forms.BooleanField(label="I am a doctor", required=False)

    # def save(self, request):
    #     user = super(CustomSignupForm, self).save(request)
    #     user.is_doctor = self.cleaned_data.get("is_doctor")
    #     user.save()
    #     return user
    pass


class UploadHistoryForm(forms.ModelForm):
    platform = forms.ChoiceField(
        label="정상방식 구분",
        choices=get_platform_choices(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = UploadHistory
        fields = [
            "name",
            "platform",
            "ayear",
            "amonth",
            "afile",
        ]

    def __init__(self, *args, **kwargs):
        super(UploadHistoryForm, self).__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["platform"].required = True
        self.fields["ayear"].required = True
        self.fields["amonth"].required = True
        self.fields["afile"].required = True


class MagamMasterForm(forms.ModelForm):
    class Meta:
        model = MagamMaster
        fields = [
            "ayear",
            "amonth",
            # "target_rows",
        ]

    def __init__(self, *args, **kwargs):
        super(MagamMasterForm, self).__init__(*args, **kwargs)
        self.fields["ayear"].required = True
        self.fields["amonth"].required = True
