from django import forms
from django.forms import ModelForm
from collab.models import Refers, ReferHistory
from customer.models import Company
import datetime


class CollabCompanyForm(ModelForm):

    class Meta:
        model = Company
        fields = "__all__"
        exclude = [
            "customuser",
            "created_at",
            "updated_at",
            "is_clinic",
            "is_collab",
            "is_active",
            "deleted_at",
        ]
        error_messages = {
            "business_name": {
                "required": "병원명을 반드시 입력해주세요.",
            },
            # Add other fields and their error messages as needed
        }


class ReferForm(ModelForm):
    class Meta:
        model = Refers
        fields = "__all__"
        exclude = [
            "company",
            "created_at",
            "updated_at",
            "provider",
            "opinion2",
            "opinioned_at",
        ]

        # target_date = forms.DateField(
        #     input_formats=["%Y-%m-%d"],
        #     widget=forms.DateInput(attrs={"type": "date"}),
        #     required=False,
        # )

    referred_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        initial=datetime.date.today(),
    )

    # patient_name = forms.CharField(
    #     widget=forms.TextInput(attrs={"class": "form-control"}),
    #     required=True,
    # )

    # patient_birthdate = forms.DateField(
    #     input_formats=["%Y-%m-%d"],
    #     widget=forms.DateInput(attrs={"type": "date"}),
    #     required=True,
    # )
