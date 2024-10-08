import pandas as pd
from django.shortcuts import render
from minibooks.models import (
    UploadHistory,
    ReportMaster,
    ReportMasterStat,
    ReportMasterPerformance,
    MagamAccounting,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .filters import ReportFilter
from django.db.models import Count, Sum, Q, F, Func, Avg
from django.db.models.functions import Collate
from django.db import connection
from accounts.models import Profile, CustomUser
from customer.models import Company


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
    # count_rpms = rpms.count()

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

    total_by_amodality = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=radio)
        .values("amodality")
        .annotate(
            total_price=Sum("readprice"),
            total_provider=Sum("pay_to_provider"),
            total_human=Sum("pay_to_human"),
            total_cases=Count("case_id"),
        )
        .order_by("amodality")
    )

    provider = CustomUser.objects.get(id=radio)
    companies = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=radio)
        .values("company__business_name")
        .distinct()
    )
    count_rpms = companies.count()

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
        "total_by_amodality": total_by_amodality,
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


def partial_pivot_table_view(request, ayear, amonth):
    # Get query parameters (if any)
    company_filter = request.GET.get("company_id", None)

    # Fetch data from the model and ensure you only fetch the required fields
    data = (
        ReportMasterPerformance.objects.filter(ayear=ayear, amonth=amonth)
        .exclude(company_id=1)
        .values("amodality", "time_range", "frequency")
        .order_by("time_range", "amodality")
    )

    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    companies = Company.objects.all().order_by(ko_kr.asc())
    selected_company = companies.filter(id=company_filter).first()

    # Apply filtering if company_filter is specified
    if company_filter:
        data = data.filter(company_id=company_filter)

    # Convert queryset to a list of dictionaries
    df = pd.DataFrame.from_records(data)

    if df.empty:
        pivot_html = "<p>No data available for the selected filters.</p>"
    else:
        # Create the pivot table
        # Define the desired order of columns
        desired_order = ["2h", "1d", "2d", "7d", "7d+"]

        # Create the pivot table with ordered columns
        pivot_df = pd.pivot_table(
            df,
            values="frequency",
            index="amodality",
            columns="time_range",
            aggfunc="sum",
            fill_value=0,
        )

        # Reorder the columns
        pivot_df = pivot_df.reindex(columns=desired_order)

        # Convert the pivot table to HTML
        pivot_html = pivot_df.to_html(classes="table table-zebra table-hover")

        # var datact = {{rs_time_dataset_ct|safe}};
        # var datamr = {{rs_time_dataset_mr|safe}};
        # var datacr = {{rs_time_dataset_cr|safe}};
        # var labels = ['1hrs','3hrs','1day', '3days', '7days', 'Above'];

        v_labels = ""
        v_datact = ""
        v_datamr = ""
        v_datacr = ""

        for index, row in pivot_df.iterrows():
            # print(f"Modality: {index}")
            v_labels += f"'{index}',"
            if index == "CT":
                v_datact += f"{list(row)}"
            elif index == "MR":
                v_datamr += f"{list(row)}"
            else:
                v_datacr += f"{list(row)}"
        v_labels = "['2h','1d','2d', '7d', '7d+']"

        # print(v_labels)
        # print(v_datacr)
        # print(v_datact)
        # print(v_datamr)

        # for time_range, frequency in row.items():
        #     print(f"  Time Range: {time_range}, Frequency: {frequency}")

    context = {
        "pivot_table": pivot_html,
        "ayear": ayear,
        "amonth": amonth,
        "companies": companies,
        "selected_company": selected_company,
        "v_labels": v_labels,
        "v_datact": v_datact,
        "v_datamr": v_datamr,
        "v_datacr": v_datacr,
    }
    # print(selected_company)
    return render(request, "report/partial_pivot_template.html", context)


def accounting(request):
    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {"buttons_year_month": buttons_year_month}

    return render(request, "report/accounting.html", context)


def accounting_month(request, ayear, amonth):

    rs_ma = MagamAccounting.objects.filter(ayear=ayear, amonth=amonth)

    rs_ma_revenue = rs_ma.filter(account_code="100")
    rs_ma_revenue_total = rs_ma_revenue.aggregate(Sum("account_total"))[
        "account_total__sum"
    ]
    rs_ma_revenue_total = rs_ma_revenue_total if rs_ma_revenue_total else 0

    rs_ma_expense = rs_ma.filter(account_code="200")
    rs_ma_expense_total = rs_ma_expense.aggregate(Sum("account_total"))[
        "account_total__sum"
    ]
    rs_ma_expense_total = rs_ma_expense_total if rs_ma_expense_total else 0

    rs_ma_revenue_clients = rs_ma.filter(account_code="100").values(
        "client__business_name", "account_total"
    )
    rs_ma_expense_providers = rs_ma.filter(account_code="200").values(
        "provider__profile__real_name", "account_total"
    )

    context = {
        "rs_ma_revenue_total": rs_ma_revenue_total,
        "rs_ma_expense_total": rs_ma_expense_total,
        "rs_ma_profit": rs_ma_revenue_total - rs_ma_expense_total,
        "rs_ma_revenue_clients": rs_ma_revenue_clients,
        "rs_ma_expense_providers": rs_ma_expense_providers,
        "ayear": ayear,
        "amonth": amonth,
    }

    return render(request, "report/accounting_month.html", context)
