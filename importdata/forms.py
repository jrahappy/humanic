from django import forms
from .models import importhistory


class importhistoryForm(forms.ModelForm):
    class Meta:
        model = importhistory
        fields = [
            "user",
            "ayear",
            "amonth",
            "source_from",
            "description",
            "file",
        ]

    def __init__(self, *args, **kwargs):
        super(importhistoryForm, self).__init__(*args, **kwargs)
        self.fields["user"].required = True
        self.fields["ayear"].required = True
        self.fields["amonth"].required = True
        self.fields["source_from"].required = True
        # self.fields['description'].required = True
        self.fields["file"].required = True

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     # Perform any additional processing or validation here
    #     if commit:
    #         instance.save()
    #     return instance
