from django.forms import ModelForm
from django import forms
from .models import Opportunity, Chance


class OpportunityForm(ModelForm):
    target_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )

    class Meta:
        model = Opportunity
        fields = "__all__"
        exclude = [
            "created_at",
            "deleted_at",
            "company",
            "agent",
        ]


class ChanceForm(ModelForm):
    class Meta:
        model = Chance
        fields = "__all__"
        exclude = ["agent", "created_at"]
