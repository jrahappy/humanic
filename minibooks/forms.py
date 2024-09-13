from django import forms
from .models import UploadHistory


class UploadHistoryForm(forms.ModelForm):
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

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     # Perform any additional processing or validation here
    #     if commit:
    #         instance.save()
    #     return instance
