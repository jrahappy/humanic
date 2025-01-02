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


class CollabCompanyForm(ModelForm):

    class Meta:
        model = Company
        # fields = [
        #     "referred_date",
        #     "patient_name",
        #     "patient_gender",
        #     "patient_birthdate",
        #     "patient_phone",
        #     "opinion1",
        # ]
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
        fields = [
            # "company",
            "referred_date",
            "patient_name",
            "patient_gender",
            "patient_birthdate",
            "patient_phone",
            "opinion1",
        ]
        # fields = "__all__"
        # exclude = [
        #     "company",
        #     "created_at",
        #     "updated_at",
        #     "provider",
        #     "opinion2",
        #     "opinioned_at",
        #     "status",
        # ]

    referred_date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        initial=datetime.date.today(),
        validators=[
            MinValueValidator(datetime.date(1900, 1, 1)),
            MaxValueValidator(datetime.date.today(), message="날짜를 확인해주십시오"),
        ],
    )
    patient_phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
                message="숫자,.,-,+,() 기호만 허용. 예) 02-1234-5678, 010-1234-5678, +82-10-1234-5678",
            )
        ],
    )
    patient_gender = forms.ChoiceField(
        choices=[("", "선택"), ("M", "Male"), ("F", "Female")],
        required=True,
        error_messages={
            "required": "성별을 선택해주세요.",
        },
    )
    patient_birthdate = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
        validators=[
            MinValueValidator(datetime.date(1900, 1, 1)),
            MaxValueValidator(datetime.date.today(), message="날짜를 확인해주십시오"),
        ],
    )
    # directions = forms.CharField(
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
            # "opinioned_at",
            "opinion2",
            "status",
            "readprice",
            "url",
            # Add other fields as necessary
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
