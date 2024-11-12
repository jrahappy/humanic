import pandas as pd
from django.shortcuts import render
from minibooks.models import (
    UploadHistory,
    ReportMaster,
    ReportMasterStat,
    ReportMasterPerformance,
    MagamAccounting,
    MagamMaster,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Sum, Q, Func
import plotly.express as px
from accounts.models import CustomUser
from customer.models import Company
from utils.base_func import get_specialty_choices
from collections import defaultdict


def monthly_pro_cus(request):

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {"buttons_year_month": buttons_year_month}

    return render(request, "report/report_monthly_pro_cus.html", context)


def report_pro_cus(request, ayear, amonth):

    # rs = ReportMasterStat.objects.all()
    rs = ReportMasterStat.objects.filter(ayear=ayear, amonth=amonth)

    # 매출 구하기
    revenue_total = rs.aggregate(revenue_sum=Sum("total_revenue"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 병원별 통계
    rs_cm = (
        rs.values("company__business_name", "company")
        .annotate(
            company_count=Sum("total_count"),  # Summing total_count per modality
            company_total=Sum("total_revenue"),
        )
        .order_by("-company_total")
    )
    # 판독의별 통계
    rs_dr = (
        rs.values("provider__profile__real_name", "provider")
        .annotate(
            provider_count=Sum("total_count"),  # Summing total_count per modality
            provider_total=Sum("total_revenue"),
        )
        .order_by("-provider_total")
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {
        "ayear": ayear,
        "amonth": amonth,
        "revenue_total_value": revenue_total_value,
        "rs_cm": rs_cm,
        "rs_dr": rs_dr,
        "buttons_year_month": buttons_year_month,
    }

    return render(request, "report/partial_pro_cus.html", context)


def partial_customer_by_month(request, ayear, company):

    # 년도별 그래프 자료
    stat = ReportMaster.objects.filter(ayear=ayear, company=company)
    business_name = stat.first().apptitle

    stat_agg_by_amodality = (
        stat.values("ayear", "amonth", "amodality")
        .annotate(total_revenue=Sum("readprice"))
        .order_by("amodality")
    )
    x_values = [
        f"{entry['ayear']}-{str(entry['amonth']).zfill(2)}"
        for entry in stat_agg_by_amodality
    ]

    # Get the modality and total_revenue
    amodalities = stat_agg_by_amodality.values_list(
        "amodality", flat=True
    )  # Amodality for each bar
    total_revenue = stat_agg_by_amodality.values_list(
        "total_revenue", flat=True
    )  # Y-axis values

    # Create the bar chart with ayear-amonth and amodality on the x-axis
    fig = px.bar(
        x=x_values,
        y=total_revenue,
        color=amodalities,  # Group by amodality
        labels={
            "x": "Year-Month",
            "y": "Total Revenue",
            "color": "Modality",
        },
        title="2024년",
        barmode="group",  # Group bars by modality within each month
    )

    # Use `bargap` to adjust bar spacing, not `width`
    fig.update_layout(
        autosize=True,
        width=None,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        barmode="stack",
        # bargap=0.2,  # Adjust space between grouped bars
        # autosize=True,  # Enable responsive sizing
        # # height=600,  # Set the overall plot height in pixels
    )

    chart = fig.to_html()
    # Convert the chart to HTML
    context = {
        "ayear": ayear,
        "business_name": business_name,
        "chart": chart,
    }

    return render(request, "report/partial_customer_by_month.html", context)


def partial_provider_by_month(request, ayear, provider):

    # 년도별 그래프 자료
    stat = ReportMaster.objects.filter(ayear=ayear, provider=provider)
    radiologist = stat.first().radiologist

    stat_agg_by_amodality = (
        stat.values("ayear", "amonth", "amodality")
        .annotate(total_revenue=Sum("readprice"))
        .order_by("amodality")
    )
    x_values = [
        f"{entry['ayear']}-{str(entry['amonth']).zfill(2)}"
        for entry in stat_agg_by_amodality
    ]

    # Get the modality and total_revenue
    amodalities = stat_agg_by_amodality.values_list(
        "amodality", flat=True
    )  # Amodality for each bar
    total_revenue = stat_agg_by_amodality.values_list(
        "total_revenue", flat=True
    )  # Y-axis values

    # Create the bar chart with ayear-amonth and amodality on the x-axis
    fig = px.bar(
        x=x_values,
        y=total_revenue,
        color=amodalities,  # Group by amodality
        labels={
            "x": "Year-Month",
            "y": "Total Revenue",
            "color": "Modality",
        },
        title="2024년",
        barmode="group",  # Group bars by modality within each month
    )

    # Use `bargap` to adjust bar spacing, not `width`
    fig.update_layout(
        autosize=True,
        width=None,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        barmode="stack",
        # bargap=0.2,  # Adjust space between grouped bars
        # autosize=True,  # Enable responsive sizing
        # # height=600,  # Set the overall plot height in pixels
    )

    chart = fig.to_html()
    # Convert the chart to HTML
    context = {
        "ayear": ayear,
        "radiologist": radiologist,
        "chart": chart,
    }

    return render(request, "report/partial_provider_by_month.html", context)


def partial_provider_by_month_pivot(request, ayear, amonth, provider):

    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, provider=provider)
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
        .order_by("company__business_name", "amodality")
    )
    provider = CustomUser.objects.get(id=provider)
    real_name = provider.profile.real_name
    df = pd.DataFrame(rpms)
    if df.empty:
        pivot_html = None
    else:
        pivot = pd.pivot_table(
            df,
            index=["company__business_name"],
            columns=["amodality"],
            values=[
                "total_price",
                "total_cases",
            ],
            aggfunc={
                "total_price": "sum",
                "total_cases": "sum",
            },
            margins=True,
            margins_name="Total",
        )
        # Format the values
        pivot["total_price"] = (
            pivot["total_price"]
            .fillna(0)
            .astype(int)
            .map(lambda x: f"{x:,.0f}")  # Apply formatting
        )
        pivot["total_cases"] = (
            pivot["total_cases"].fillna(0).astype(int).map(lambda x: f"{x:,.0f}")
        )

        pivot_html = pivot.to_html(classes="table table-zebra table-sm table-hover")
    # Convert the chart to HTML
    context = {
        "ayear": ayear,
        "amonth": amonth,
        "radiologist": real_name,
        "pivot_html": pivot_html,
    }

    return render(request, "report/partial_provider_by_month_pivot.html", context)


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
        "company__business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    # buttons_customer = Company.objects.filter(is_clinic=True).order_by(ko_kr.asc())

    rs = (
        ReportMasterStat.objects.filter(company__is_clinic=True)
        .values("company", "company__business_name", "company_id")
        .annotate(
            total_revenue=Sum("total_revenue"),
            total_count=Sum("total_count"),
        )
        .order_by(ko_kr.asc())
    )

    context = {"rs": rs}

    return render(request, "report/report_customer.html", context)


def partial_search_customer(request):
    q = request.GET.get("q", "").strip()
    ko_kr = Func(
        "company__business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )

    if q:
        buttons_customer = (
            ReportMasterStat.objects.filter(
                company__is_clinic=True, company__business_name__icontains=q
            )
            .values("company", "company__business_name", "company_id")
            .annotate(
                total_revenue=Sum("total_revenue"),
                total_count=Sum("total_count"),
            )
            .order_by(ko_kr.asc())
        )
    else:
        buttons_customer = (
            ReportMasterStat.objects.filter(company__is_clinic=True)
            .values("company", "company__business_name", "company_id")
            .annotate(
                total_revenue=Sum("total_revenue"),
                total_count=Sum("total_count"),
            )
            .order_by(ko_kr.asc())
        )
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
    # report_filter = ReportFilter(
    #     request.GET,
    #     # queryset=ReportMaster.objects.all().select_related("provider", "company"),
    #     queryset=ReportMaster.objects.prefetch_related("provider", "company"),
    # )
    # filtered_qs = report_filter.qs.order_by("-ayear", "-amonth", "-created_at")[0:10]
    search_query = request.GET.get("search", "").strip()
    if search_query:
        report_qs = ReportMaster.objects.filter(
            Q(case_id__icontains=search_query) | Q(name__icontains=search_query)
        )
    else:
        report_qs = ReportMaster.objects.all()[0:10]

    paginator = Paginator(report_qs, 10)
    page = request.GET.get("page")
    try:
        rmaster = paginator.page(page)
    except PageNotAnInteger:
        rmaster = paginator.page(1)
    except EmptyPage:
        rmaster = paginator.page(paginator.num_pages)

    context = {"rmaster": rmaster, "search": search_query}

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

    stat = ReportMasterStat.objects.filter(provider=radio)
    stat_agg_by_amodality = (
        stat.values("ayear", "amonth", "amodality")
        .annotate(total_revenue=Sum("total_revenue"))
        .order_by("amodality")
    )
    x_values = [
        f"{entry['ayear']}-{str(entry['amonth']).zfill(2)}"
        for entry in stat_agg_by_amodality
    ]

    # Get the modality and total_revenue
    amodalities = stat_agg_by_amodality.values_list(
        "amodality", flat=True
    )  # Amodality for each bar
    total_revenue = stat_agg_by_amodality.values_list(
        "total_revenue", flat=True
    )  # Y-axis values

    # Create the bar chart with ayear-amonth and amodality on the x-axis
    fig = px.bar(
        x=x_values,
        y=total_revenue,
        color=amodalities,  # Group by amodality
        labels={
            "x": "Year-Month",
            "y": "Total Revenue",
            "color": "Modality",
        },
        title="과거 3개원간의 판독매출 흐름",
        barmode="group",  # Group bars by modality within each month
    )

    # Use `bargap` to adjust bar spacing, not `width`
    fig.update_layout(
        bargap=0.2,  # Adjust space between grouped bars
        width=800,  # Set the overall plot width in pixels
        height=600,  # Set the overall plot height in pixels
    )

    chart = fig.to_html()
    # Convert the chart to HTML

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
        "chart": chart,
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


def chart(request):
    # Fetch all records
    stat = ReportMasterStat.objects.all()
    stat_agg_by_amodality = (
        stat.values("ayear", "amonth", "amodality")
        .annotate(total_revenue=Sum("total_revenue"))
        .order_by("amodality")
    )
    # Create a list of 'ayear-amonth' for grouping by year and month
    x_values = [
        f"{entry['ayear']}-{str(entry['amonth']).zfill(2)}"
        for entry in stat_agg_by_amodality
    ]

    # Get the modality and total_revenue
    amodalities = stat_agg_by_amodality.values_list(
        "amodality", flat=True
    )  # Amodality for each bar
    total_revenue = stat_agg_by_amodality.values_list(
        "total_revenue", flat=True
    )  # Y-axis values

    # Create the bar chart with ayear-amonth and amodality on the x-axis
    fig = px.bar(
        x=x_values,
        y=total_revenue,
        color=amodalities,  # Group by amodality
        labels={
            "x": "Year-Month",
            "y": "Total Revenue",
            "color": "Modality",
        },  # Axis labels
        text_auto=True,
        title="Monthly Revenue by Modality",
        barmode="group",  # Group bars by modality within each month
    )

    # Convert the chart to HTML
    chart = fig.to_html()

    # Pass the chart to the template context
    context = {
        "chart": chart,
    }
    # context = {}
    return render(request, "report/chart.html", context)


def rad_by_subspecialty(request):
    # Prefetch profile with related specialties and pre-compute `total_readprice` for each user
    latest_magam = MagamMaster.objects.latest("created_at")
    latest_year = latest_magam.ayear
    latest_month = latest_magam.amonth
    latest_year_magam_count = MagamMaster.objects.filter(ayear=latest_year).count()

    rads = (
        CustomUser.objects.filter(is_doctor=True, is_active=True)
        # .exclude(profile__specialty2__isnull=True)
        .select_related(
            "profile"
        ).annotate(  # Ensure profile is loaded to avoid extra queries
            total_readprice=Sum(
                "reportmasterstat__total_revenue",
                filter=Q(reportmasterstat__ayear=latest_year),
            ),
            latest_month_total_revenue=Sum(
                "reportmasterstat__total_revenue",
                filter=Q(reportmasterstat__amonth=latest_month)
                & Q(reportmasterstat__ayear=latest_year),
            ),  # Calculate total revenue for September for each doctor
        )
    )

    # Dictionary to store doctors grouped by subspecialty
    grouped_by_subspecialty = defaultdict(list)

    # Populate the dictionary with subspecialties as keys and doctors as values
    for rad in rads:

        latest_month_total = rad.latest_month_total_revenue or 0
        total_readprice = rad.total_readprice or 0

        # Avoid division by zero
        if latest_year_magam_count != 0:
            average_revenue = total_readprice / latest_year_magam_count
        else:
            average_revenue = 0

        # Determine the trend
        if latest_month_total != 0:
            if (average_revenue / latest_month_total) > 1.1:
                trend = "down"
            elif (average_revenue / latest_month_total) < 0.9:
                trend = "up"
            else:
                trend = "equal"
        else:
            trend = "equal"

        specialty_name = rad.profile.specialty2
        grouped_by_subspecialty[specialty_name].append(
            {
                "user": rad,
                "real_name": rad.profile.real_name,
                "contract_status": rad.profile.contract_status,
                "total_readprice": rad.total_readprice or 0,  # Default to 0 if null
                "latest_month_total_revenue": rad.latest_month_total_revenue or 0,
                "trend": trend,
            }
        )

    # Convert defaultdict to a regular dictionary
    grouped_by_subspecialty = dict(grouped_by_subspecialty)

    # Count doctors for each subspecialty
    counts_by_subspecialty = {
        key: len(value) for key, value in grouped_by_subspecialty.items()
    }

    context = {
        "grouped_by_subspecialty": grouped_by_subspecialty,
        "counts_by_subspecialty": counts_by_subspecialty,
        "latest_year": latest_year,
        "latest_month": latest_month,
    }
    return render(request, "report/rad_by_subspecialty.html", context)
