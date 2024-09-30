from django.shortcuts import render
from minibooks.models import UploadHistory, ReportMaster, ReportMasterStat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ReportFilter
from django.db.models import Count, Sum, Q, F, Func, Avg
from accounts.models import Profile, CustomUser
from customer.models import Company
from django.db.models.functions import Collate


def report_customer_detail(request, id):
    ko_kr = Func(
        "provider__profile__real_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    company = Company.objects.get(id=id)
    rpms = ReportMasterStat.objects.filter(company=company).order_by("-created_at")
    rpms_agg = (
        rpms.values("ayear", "amonth", "amodality")
        .annotate(
            t_count=Sum("total_count"),
            # avg_price=F("total_revenue") / F("total_count"),
            t_revenue=Sum("total_revenue"),
        )
        .order_by("ayear", "amonth", "amodality")
    )

    tt_count_array = rpms_agg.aggregate(Sum("t_count"))
    tt_count = tt_count_array["t_count__sum"]
    tt_revenue_array = rpms_agg.aggregate(Sum("t_revenue"))
    tt_revenue = tt_revenue_array["t_revenue__sum"]

    rs_by_provider = (
        rpms.values(
            "ayear", "amonth", "amodality", "provider__profile__real_name", "provider"
        )
        .annotate(
            total_count=Sum("total_count"),
            total_revenue=Sum("total_revenue"),
        )
        .order_by("ayear", "amonth", "amodality", ko_kr.asc())
    )

    context = {
        "rpms_agg": rpms_agg,
        "tt_count": tt_count,
        "tt_revenue": tt_revenue,
        "company": company,
        "rs_by_provider": rs_by_provider,
    }

    return render(request, "report/report_customer_detail.html", context)


def report_customer(request):
    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    buttons_customer = Company.objects.all().order_by(ko_kr.asc())
    context = {"buttons_customer": buttons_customer}

    return render(request, "report/report_customer.html", context)


def partial_search_customer(request):
    q = request.GET.get("q", "").strip()
    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    if q:
        buttons_customer = Company.objects.filter(business_name__icontains=q).order_by(
            ko_kr.asc()
        )
    else:
        buttons_customer = Company.objects.all().order_by(ko_kr.asc())

    context = {
        "buttons_customer": buttons_customer,
    }

    return render(request, "report/partial_search_customer.html", context)


def partial_search_provider(request):
    ayear = request.GET.get("ayear")
    amonth = request.GET.get("amonth")
    q = request.GET.get("q", "")

    rpms = (
        ReportMaster.objects.filter(
            ayear=ayear, amonth=amonth, provider__profile__real_name__icontains=q
        )
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
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

    rp_humans = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=1)
        .filter(Q(provider__profile__real_name__icontains=q))
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values("provider")
        .annotate(
            human_total_price=Sum("readprice"),
            human_total_provider=Sum("pay_to_provider"),
            human_total_human=Sum("pay_to_human"),
            human_total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name")
    )

    context = {
        "rpms": rpms,
        "rp_humans": rp_humans,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        # "companies": companies,
    }

    return render(request, "report/partial_search_provider.html", context)


def partial_search_provider_t(request):
    ayear = request.GET.get("ayear")
    amonth = request.GET.get("amonth")
    q = request.GET.get("q", "")

    rpms = (
        ReportMaster.objects.filter(
            ayear=ayear, amonth=amonth, provider__profile__real_name__icontains=q
        )
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
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

    rp_humans = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=1)
        .filter(Q(provider__profile__real_name__icontains=q))
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values("provider")
        .annotate(
            human_total_price=Sum("readprice"),
            human_total_provider=Sum("pay_to_provider"),
            human_total_human=Sum("pay_to_human"),
            human_total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name")
    )

    context = {
        "rpms": rpms,
        "rp_humans": rp_humans,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        # "companies": companies,
    }

    return render(request, "report/partial_search_provider_t.html", context)


def index(request):
    # report_filter = ReportFilter(request.GET, queryset=rmaster)
    report_filter = ReportFilter(request.GET, queryset=ReportMaster.objects.all())
    filtered_qs = report_filter.qs.order_by("-ayear", "-amonth", "-created_at")

    paginator = Paginator(filtered_qs, 10)
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
        .order_by("-ayear", "-amonth")
    )

    context = {"buttons_year_month": buttons_year_month}

    return render(request, "report/report_period.html", context)


def report_period_month(request, ayear, amonth):

    ko_kr = Func(
        "provider__profile__real_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth)
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values(
            "provider__profile__real_name", "provider"
        )  # Use the related field's real_name
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
        .order_by(ko_kr.asc())
    )
    count_rpms = rpms.count()

    rp_humans = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=1)
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values("provider")
        .annotate(
            human_total_price=Sum("readprice"),
            human_total_provider=Sum("pay_to_provider"),
            human_total_human=Sum("pay_to_human"),
            human_total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name")
    )

    human_total_provider_total = rp_humans.aggregate(
        total=Sum("human_total_provider"),
    )["total"]

    context = {
        "rpms": rpms,
        "rp_humans": rp_humans,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "rp_humans_total": human_total_provider_total,
        # "companies": companies,
    }

    return render(request, "report/report_period_month.html", context)


def report_period_month_table(request, ayear, amonth):
    ko_kr = Func(
        "provider__profile__real_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )

    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth)
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values(
            "provider__profile__real_name", "provider"
        )  # Use the related field's real_name
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
        .order_by(ko_kr.asc())
    )
    count_rpms = rpms.count()

    rp_humans = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=1)
        .exclude(Q(provider=72) | Q(provider=73))  # Exclude 상근원장단(이재희, 김성현)
        .values("provider")
        .annotate(
            human_total_price=Sum("readprice"),
            human_total_provider=Sum("pay_to_provider"),
            human_total_human=Sum("pay_to_human"),
            human_total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name")
    )

    human_total_provider_total = rp_humans.aggregate(
        total=Sum("human_total_provider"),
    )["total"]

    # print(human_total_provider_total)
    # print(rp_humans.count())

    context = {
        "rpms": rpms,
        "rp_humans": rp_humans,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "rp_humans_total": human_total_provider_total,
        # "companies": companies,
    }

    return render(request, "report/report_period_month_table.html", context)


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
            r_total_price=Sum("readprice"),
            r_total_provider=Sum("pay_to_provider"),
            r_total_human=Sum("pay_to_human"),
            r_total_cases=Count("case_id"),
        )
        .order_by("company__business_name", "amodality")
    )
    count_rpms = rpms.count()

    # 일반 판독금액 합계
    total_by_onsite = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=radio)
        .values("is_take")
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
        .order_by("is_onsite")
    )

    provider = CustomUser.objects.get(id=radio)
    companies = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=radio)
        .values("company__business_name")
        .distinct()
    )

    context = {
        "rpms": rpms,
        "radio": radio,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "radio": radio,
        "companies": companies,
        "provider": provider,
        "total_by_onsite": total_by_onsite,
    }

    return render(request, "report/report_period_month_radiologist.html", context)


def report_period_month_radiologist_detail(
    request, ayear, amonth, provider, company, amodality
):
    rpms = ReportMaster.objects.filter(
        ayear=ayear,
        amonth=amonth,
        provider=provider,
        company__business_name=company,
        amodality=amodality,
    ).order_by("case_id")[:500]
    count_rpms = rpms.count()
    # s_provider = CustomUser.objects.get(id=radio)
    print(provider)
    provider = CustomUser.objects.get(id=provider)
    print("new provider:", provider.id)
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


def performance(request):

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {"buttons_year_month": buttons_year_month}

    return render(request, "report/performance.html", context)


def partial_performance_month(request, ayear, amonth):

    # ko_kr = Func(
    #     "provider__profile__real_name",
    #     function="ko_KR.utf8",
    #     template='(%(expressions)s) COLLATE "%(function)s"',
    # )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=ayear, amonth=amonth)
    rs_ct_time = rs_graph.filter(amodality="CT")
    rs_ct_time_1hr = rs_ct_time.filter(
        time_to_complete__gte=1, time_to_complete__lte=60
    ).count()
    rs_ct_time_3hr = rs_ct_time.filter(
        time_to_complete__gt=60, time_to_complete__lte=180
    ).count()
    rs_ct_time_1d = rs_ct_time.filter(
        time_to_complete__gt=180, time_to_complete__lte=1440
    ).count()
    rs_ct_time_3d = rs_ct_time.filter(
        time_to_complete__gt=1440, time_to_complete__lte=4320
    ).count()
    rs_ct_time_7d = rs_ct_time.filter(
        time_to_complete__gt=4320, time_to_complete__lte=10080
    ).count()
    rs_ct_time_more = rs_ct_time.filter(time_to_complete__gt=10080).count()

    rs_mr_time = rs_graph.filter(amodality="MR")
    rs_mr_time_1hr = rs_mr_time.filter(
        time_to_complete__gte=1, time_to_complete__lte=60
    ).count()
    rs_mr_time_3hr = rs_mr_time.filter(
        time_to_complete__gt=60, time_to_complete__lte=180
    ).count()
    rs_mr_time_1d = rs_mr_time.filter(
        time_to_complete__gt=180, time_to_complete__lte=1440
    ).count()
    rs_mr_time_3d = rs_mr_time.filter(
        time_to_complete__gt=1440, time_to_complete__lte=4320
    ).count()
    rs_mr_time_7d = rs_mr_time.filter(
        time_to_complete__gt=4320, time_to_complete__lte=10080
    ).count()
    rs_mr_time_more = rs_mr_time.filter(time_to_complete__gt=10080).count()

    rs_cr_time = rs_graph.filter(amodality="CR")
    rs_cr_time_1hr = rs_cr_time.filter(
        time_to_complete__gte=1, time_to_complete__lte=60
    ).count()
    rs_cr_time_3hr = rs_cr_time.filter(
        time_to_complete__gt=60, time_to_complete__lte=180
    ).count()
    rs_cr_time_1d = rs_cr_time.filter(
        time_to_complete__gt=180, time_to_complete__lte=1440
    ).count()
    rs_cr_time_3d = rs_cr_time.filter(
        time_to_complete__gt=1440, time_to_complete__lte=4320
    ).count()
    rs_cr_time_7d = rs_cr_time.filter(
        time_to_complete__gt=4320, time_to_complete__lte=10080
    ).count()
    rs_cr_time_more = rs_cr_time.filter(time_to_complete__gt=10080).count()

    rs_time_dataset_ct = [
        rs_ct_time_1hr,
        rs_ct_time_3hr,
        rs_ct_time_1d,
        rs_ct_time_3d,
        rs_ct_time_7d,
        rs_ct_time_more,
    ]
    rs_time_dataset_mr = [
        rs_mr_time_1hr,
        rs_mr_time_3hr,
        rs_mr_time_1d,
        rs_mr_time_3d,
        rs_mr_time_7d,
        rs_mr_time_more,
    ]
    rs_time_dataset_cr = [
        rs_cr_time_1hr,
        rs_cr_time_3hr,
        rs_cr_time_1d,
        rs_cr_time_3d,
        rs_cr_time_7d,
        rs_cr_time_more,
    ]

    context = {
        "rs_graph": rs_graph,
        "ayear": ayear,
        "amonth": amonth,
        "rs_time_dataset_ct": rs_time_dataset_ct,
        "rs_time_dataset_mr": rs_time_dataset_mr,
        "rs_time_dataset_cr": rs_time_dataset_cr,
    }

    return render(request, "report/partial_performance_month.html", context)
