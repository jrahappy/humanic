from django.contrib.auth import get_user_model
from django.forms import ModelForm
from accounts.models import Profile, CustomUser


class ProviderForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            # "user",
            "real_name",
            "specialty1",
            "specialty2",
            "specialty3",
            "specialty4",
            "specialty5",
            "position",
            "email",
            "cv3_id",
            "onpacs_id",
            "bio",
            "cellphone",
            # "company",
            "employee_id",
            "fee_rate",
        ]
