from django.forms import ModelForm, inlineformset_factory
from .models import MegaChoices, MegaChoiceNames


class MegaChoicesForm(ModelForm):
    class Meta:
        model = MegaChoices
        fields = "__all__"


MegaChoicesFormSet = inlineformset_factory(
    MegaChoiceNames, MegaChoices, form=MegaChoicesForm, extra=1
)
