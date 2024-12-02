from django.forms import ModelForm
from django import forms
from .models import Opportunity, Chance
from accounts.models import CustomUser


class OpportunityForm(ModelForm):
    target_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )
    agent = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(
            is_staff=True, is_active=True, is_privacy=False
        ),
        empty_label="Select",
        widget=forms.Select(attrs={"class": "form-control"}),
        to_field_name="id",
        required=True,
        error_messages={"required": "Please select an agent."},
    )

    class Meta:
        model = Opportunity
        fields = "__all__"
        exclude = [
            "created_at",
            "deleted_at",
            "company",
        ]


class ChanceForm(ModelForm):
    class Meta:
        model = Chance
        fields = "__all__"
        exclude = ["agent", "created_at"]
