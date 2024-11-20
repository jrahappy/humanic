from django.forms import ModelForm
from django import forms
from django.db.models import Func
from .models import Company, ServiceFee, CustomerLog, CustomerContact
from django.core.exceptions import ValidationError


class CustomerContactForm(ModelForm):
    class Meta:
        model = CustomerContact
        fields = "__all__"
        exclude = ["company"]


class CustomerLogForm(ModelForm):
    class Meta:
        model = CustomerLog
        fields = "__all__"
        exclude = ["company", "updated_by", "deleted_at"]


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


class ServiceFeeForm(ModelForm):
    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    service_company = forms.ModelChoiceField(
        required=True,
        label="Service Company",
        queryset=Company.objects.filter(is_clinic=False).order_by(ko_kr),
        widget=forms.Select(attrs={"readonly": "readonly"}),
    )

    def clean_service_company(self):
        service_company = self.cleaned_data.get("service_company")
        if not service_company:
            raise forms.ValidationError("Service Company cannot be empty.")
        return service_company

    class Meta:
        model = ServiceFee
        fields = "__all__"
        exclude = ["company"]
