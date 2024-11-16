from django import forms
from accounts.models import ProductionTarget


class ProductionTargetForm(forms.ModelForm):
    class Meta:
        model = ProductionTarget
        fields = "__all__"
        exclude = ["user"]

    # def cleaned_data(self):
    #     data = self.cleaned_data.get("data")
    #     if not data:
    #         raise forms.ValidationError("This field is required.")
    #     return data
