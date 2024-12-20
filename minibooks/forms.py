from django import forms
from .models import UploadHistory, MagamMaster
from utils.base_func import get_platform_choices


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
