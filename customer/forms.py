from django.forms import ModelForm
from django import forms
from django.db.models import Func
from .models import Company, ServiceFee, CustomerLog, CustomerContact, CustomerFiles
from django.core.exceptions import ValidationError

# from django_recaptcha.fields import ReCaptchaField


class CustomerFilesForm(ModelForm):
    class Meta:
        model = CustomerFiles
        fields = "__all__"
        exclude = ["company"]


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


class InquiryForm(ModelForm):
    # captcha = ReCaptchaField()

    class Meta:
        model = Company
        fields = {
            "business_name",
            "contact_person",
            "office_cellphone",
            "office_email",
            "bio",
            "is_public",
            # "captcha",
        }


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = {
            "business_name",
            "president_name",
            "ein",
            "is_clinic",
            "address",
            "suite",
            "city",
            "state",
            "country",
            "zipcode",
            "office_phone",
            "office_cellphone",
            "office_fax",
            "office_email",
            "website",
            "contact_person",
            "is_collab",
            "is_collab_contract",
            "is_tele",
            "tags",
        }
        # fields = "__all__"
        error_messages = {
            "business_name": {
                "required": "병원명을 반드시 입력해주세요.",
            },
            # Add other fields and their error messages as needed
        }

        # is_tele = forms.BooleanField(
        #     required=False,
        #     label="원격판독",
        #     widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        # )


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
