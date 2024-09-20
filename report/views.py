from django.shortcuts import render
from minibooks.models import UploadHistory, ReportMaster
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ReportFilter


def index(request):
    # report_filter = ReportFilter(request.GET, queryset=rmaster)
    report_filter = ReportFilter(request.GET, queryset=ReportMaster.objects.all())
    filtered_qs = report_filter.qs.order_by("-ayear", "-amonth", "-created_at")

    paginator = Paginator(filtered_qs, 100)
    page = request.GET.get("page")
    try:
        rmaster = paginator.page(page)
    except PageNotAnInteger:
        rmaster = paginator.page(1)
    except EmptyPage:
        rmaster = paginator.page(paginator.num_pages)

    context = {"rmaster": rmaster, "filter": report_filter}

    return render(request, "report/index.html", context)
