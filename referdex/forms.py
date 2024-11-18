from django.forms import ModelForm
from django import forms
from .models import ProductionMade, ProductionMadeDetail
from django.core.validators import MinValueValidator


class ProductionMadeForm(ModelForm):
    requested_qty = forms.IntegerField(
        required=True,
        label="Requested Quantity",
        initial=0,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        model = ProductionMade
        fields = "__all__"
        exclude = ["created_by", "created_at"]


class ProductionMadeDetailForm(ModelForm):
    assigned_qty = forms.IntegerField(
        required=True,
        label="Assigned Quantity",
        # initial=0,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        model = ProductionMadeDetail
        fields = "__all__"
        exclude = ["production"]
