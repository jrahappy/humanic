from django.forms import ModelForm
from .models import Company
from django import forms


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = "__all__"
        error_messages = {
            "business_name": {
                "required": "병원명을 반드시 입력해주세요.",
            },
            # Add other fields and their error messages as needed
        }
