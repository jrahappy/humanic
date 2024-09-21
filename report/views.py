from django.shortcuts import render
from minibooks.models import UploadHistory, ReportMaster
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ReportFilter
from django.db.models import Count, Sum


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


def report_period(request):

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("ayear", "amonth")
    )

    context = {"buttons_year_month": buttons_year_month}

    return render(request, "report/report_period.html", context)


def report_period_month(request, ayear, amonth):
    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth)
        .values("radiologist")  # Use the related field's real_name
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
    )
    count_rpms = rpms.count()

    context = {"rpms": rpms, "count_rpms": count_rpms, "ayear": ayear, "amonth": amonth}

    return render(request, "report/report_period_month.html", context)


def report_period_month_radiologist(request, ayear, amonth, radio):
    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, radiologist=radio)
        .values("apptitle")
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
    )
    count_rpms = rpms.count()

    context = {
        "rpms": rpms,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "radio": radio,
    }

    return render(request, "report/report_period_month_radiologist.html", context)
