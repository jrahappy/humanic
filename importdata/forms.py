from django import forms
from .models import importhistory


class importhistoryForm(forms.ModelForm):
    class Meta:
        model = importhistory
        fields = [
            "user",
            "description",
            "file",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Perform any additional processing or validation here
        if commit:
            instance.save()
        return instance
