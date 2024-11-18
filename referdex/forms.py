from django.forms import ModelForm
from django import forms
from .models import ProductionMade, ProductionMadeDetail, MatchRules
from django.core.validators import MinValueValidator
from customer.models import Company
from django.db.models import Func


class MatchRulesForm(ModelForm):

    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    company = forms.ModelChoiceField(
        required=True,
        label="Company",
        queryset=Company.objects.filter(is_clinic=True).order_by(ko_kr),
        widget=forms.Select(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = MatchRules
        fields = "__all__"
        exclude = ["created_at", "updated_at", "provider"]


class ProductionMadeForm(ModelForm):
    requested_qty = forms.IntegerField(
        required=True,
        label="Requested Quantity",
        initial=0,
        validators=[MinValueValidator(1)],
    )

    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )

    company = forms.ModelChoiceField(
        required=True,
        label="Company",
        queryset=Company.objects.filter(is_clinic=True).order_by(ko_kr),
        widget=forms.Select(attrs={"readonly": "readonly"}),
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
