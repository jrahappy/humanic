import django_filters
from django import forms
from collab.models import Refers
from customer.models import Company
from utils.base_func import GENDER, REFER_STATUS
from django_filters.widgets import RangeWidget


class RefersFilter(django_filters.FilterSet):
    # patient_name = django_filters.CharFilter(lookup_expr="icontains")
    referred_date = django_filters.DateFromToRangeFilter(
        widget=RangeWidget(
            attrs={"type": "date"},
        ),
        label="의뢰일:",
    )
    opinioned_at = django_filters.DateFromToRangeFilter(
        widget=RangeWidget(
            attrs={"type": "date"},
        ),
        label="회송일:",
    )

    class Meta:
        model = Refers
        fields = {
            "patient_name": ["icontains"],
            "status": ["exact"],
            "company__business_name": ["icontains"],
        }
