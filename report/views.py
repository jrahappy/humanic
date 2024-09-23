from django.shortcuts import render
from minibooks.models import UploadHistory, ReportMaster
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ReportFilter
from django.db.models import Count, Sum
from accounts.models import Profile, CustomUser


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
        .values(
            "provider__profile__real_name", "provider"
        )  # Use the related field's real_name
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name")
    )
    count_rpms = rpms.count()

    context = {"rpms": rpms, "count_rpms": count_rpms, "ayear": ayear, "amonth": amonth}

    return render(request, "report/report_period_month.html", context)


def report_period_month_radiologist(request, ayear, amonth, radio):
    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=radio)
        .values(
            # "platform",
            "company__business_name",
            "amodality",
            "is_onsite",
        )
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
        "radio": radio,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "radio": radio,
    }

    return render(request, "report/report_period_month_radiologist.html", context)


def report_period_month_radiologist_detail(
    request, ayear, amonth, radio, company, amodality
):
    rpms = ReportMaster.objects.filter(
        ayear=ayear,
        amonth=amonth,
        provider=radio,
        company__business_name=company,
        amodality=amodality,
    )
    count_rpms = rpms.count()
    # s_provider = CustomUser.objects.get(id=radio)
    provider = Profile.objects.get(user=radio)

    context = {
        "rpms": rpms,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "provider": provider,
        "company": company,
        "amodality": amodality,
    }

    return render(
        request, "report/report_period_month_radiologist_detail.html", context
    )
