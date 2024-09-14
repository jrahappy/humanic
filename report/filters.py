import django_filters
from minibooks.models import ReportMaster


class ReportFilter(django_filters.FilterSet):
    class Meta:
        model = ReportMaster
        fields = {
            "apptitle": ["icontains"],
            "case_id": ["icontains"],
            "name": ["icontains"],
            # "amodality": ["exact"],
            "radiologist": ["icontains"],
            "provider": ["exact"],
        }
