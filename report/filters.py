import django_filters
from minibooks.models import ReportMaster


class ReportFilter(django_filters.FilterSet):
    apptitle = django_filters.CharFilter(label="병원명", lookup_expr="icontains")
    case_id = django_filters.CharFilter(label="Case ID", lookup_expr="icontains")
    name = django_filters.CharFilter(label="환자명", lookup_expr="icontains")
    radiologist = django_filters.CharFilter(label="의사명", lookup_expr="icontains")

    class Meta:
        model = ReportMaster
        fields = {
            "apptitle",
            "case_id",
            "name",
            # "amodality": ["exact"],
            "radiologist",
        }
