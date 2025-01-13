from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

from collab.models import Refers, ReferHistory, ReferFile
from customer.models import Company
from utils.base_func import REFER_STATUS
import datetime


class ReferFileForm(ModelForm):
    class Meta:
        model = ReferFile
        fields = [
            "file",
        ]

    def clean_files(self):
        file = self.cleaned_data.get("file")
        if len(file) > 200:  # Set your desired limit
            raise ValidationError("You can upload a maximum of 200 files.")
        return file


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
            "status",
        ]

    referred_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        initial=datetime.date.today(),
        validators=[
            MinValueValidator(datetime.date(1900, 1, 1)),
            # MaxValueValidator(datetime.date.today()),
        ],
    )
    patient_birthdate = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=datetime.date.today(),
        validators=[
            MinValueValidator(datetime.date(1900, 1, 1)),
            MaxValueValidator(datetime.date.today()),
        ],
        error_messages={
            "invalid": "날짜를 확인해주세요.",
        },
    )

    patient_phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
                message="숫자,+,-,() 만 입력 가능합니다.",
            )
        ],
        error_messages={
            "required": "Please enter the patient's phone number.",
        },
    )

    # opinion1 = forms.CharField(
    #     widget=forms.Textarea(attrs={"cols": 50, "rows": 3}),
    #     required=False,
    # )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     filtered_choices = [
    #         ("Scheduled", "검사예약"),
    #         ("Cancelled", "검사취소"),
    #     ]
    #     self.fields["status"].choices = filtered_choices


class ReportForm(ModelForm):
    class Meta:
        model = Refers
        fields = [
            "opinion2",
            "status",
            "radio_doctor",
        ]

    opinioned_at = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        initial=datetime.date.today,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the filtered choices
        filtered_choices = [
            ("Interpreted", "1차판독완료"),
            # Exclude 'Cancelled', 'Interpreted', 'Cosigned', 'Archive'
        ]
        # Apply the filtered choices to the 'status' field
        self.fields["status"].choices = filtered_choices
        self.fields["radio_doctor"].initial = "휴먼영상"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filtered_choices = [
            ("Scheduled", "검사예약"),
            ("Cancelled", "검사취소"),
        ]
        self.fields["status"].choices = filtered_choices
