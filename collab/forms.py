from django import forms
from django.forms import ModelForm

# from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from collab.models import Refers, ReferHistory
from customer.models import Company
from utils.base_func import REFER_STATUS
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


class ReferForm(forms.ModelForm):
    referred_date = forms.DateField(
        input_formats=["%Y-%m-%d"],  # Updated to match HTML5 date input format
        widget=forms.DateInput(
            format="%Y-%m-%d", attrs={"type": "date"}
        ),  # Specify the correct format
        required=True,
        initial=datetime.date.today,
        # help_text="Enter the date in MM/DD/YYYY format.",
    )
    patient_phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        error_messages={
            "required": "Please enter the patient's phone number.",
        },
    )
    opinion1 = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 50, "rows": 3}),
        required=False,
    )

    class Meta:
        model = Refers
        fields = [
            "referred_date",
            "patient_name",
            "patient_birthdate",
            "patient_gender",
            "patient_phone",
            "opinion1",
            # Add other fields as necessary
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["referred_date"].initial = datetime.date.today()

    def clean_referred_date(self):
        date = self.cleaned_data["referred_date"]
        if date < datetime.date(1900, 1, 1) or date > datetime.date.today():
            raise ValidationError(
                "Please enter a valid date between 01/01/1900 and today."
            )
        return date


# class ReferForm(ModelForm):
#     class Meta:
#         model = Refers
#         fields = "__all__"
#         exclude = [
#             "company",
#             "created_at",
#             "updated_at",
#             "provider",
#             "opinion2",
#             "opinioned_at",
#         ]

#     referred_date = forms.DateField(
#         input_formats=["%m/%d/%Y"],
#         widget=forms.DateInput(attrs={"type": "date"}),
#         required=True,
#         initial=datetime.date.today,
#         validators=[
#             MinValueValidator(datetime.date(1900, 1, 1)),
#             MaxValueValidator(datetime.date.today()),
#         ],
#     )
#     patient_phone = forms.CharField(
#         max_length=20,
#         required=True,
#         error_messages={
#             "required": "Please enter the patient's phone number.",
#         },
#     )
#     directions = forms.CharField(
#         widget=forms.Textarea(attrs={"cols": 50, "rows": 3}),
#         required=False,
#     )


class ReportForm(ModelForm):
    class Meta:
        model = Refers
        fields = "__all__"
        exclude = [
            "company",
            "referred_date",
            "patient_name",
            "patient_gender",
            "patient_birthdate",
            "patient_phone",
            "illness",
            "treatment",
            "opinion1",
            "created_at",
            "updated_at",
        ]

    opinioned_at = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        initial=datetime.date.today,
    )


class ReferChangeStatus(ModelForm):
    class Meta:
        model = Refers
        fields = "scheduled_at", "status"

    scheduled_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=True,
        initial=datetime.datetime.now,
        error_messages={
            "required": "Please enter the scheduled date and time.",
            "invalid": "Enter a valid date and time.",
        },
    )
    status = forms.CharField(
        widget=forms.Select(choices=REFER_STATUS),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["status"].initial = "Scheduled"
            self.fields["scheduled_at"].initial = datetime.datetime.now()
