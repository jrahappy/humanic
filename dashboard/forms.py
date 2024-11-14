from django import forms
from accounts.models import ProductionTarget


class ProductionTargetForm(forms.ModelForm):
    class Meta:
        model = ProductionTarget
        fields = "__all__"
        exclude = ["user"]
