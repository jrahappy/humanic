from django.forms import ModelForm, forms
from accounts.models import Profile


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
            "license_number",
            "employee_id",
            "fee_rate",
        ]

    def clean_fee_rate(self):
        fee_rate = self.cleaned_data.get("fee_rate")
        if fee_rate is not None and (fee_rate < 0 or fee_rate > 1):
            raise forms.ValidationError("Fee rate must be between 0.00 and 1.00")
        return fee_rate
