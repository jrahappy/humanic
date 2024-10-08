from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Avg
from django.db.models.functions import ExtractWeekDay
from django_pivot.pivot import pivot
from django_pivot.histogram import histogram

# from importdata.models import rawdata, UploadHistory
from minibooks.models import UploadHistory, ReportMaster, ReportMasterStat
from utils.models import ChoiceMaster
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, Profile
from datetime import date


@login_required
def index(request):
    user = request.user
    # Check if the user is a staff member
    if user.is_staff:
        pass
    else:
        if user.is_doctor:
            return redirect("dashboard:index")
        else:
            return redirect("cust:index")

    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        # Fetch the latest available record from the database
        # temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth").first()
        temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth")[:2]
        # Check if any records exist in the database
        if temp_rs:
            if temp_rs.count() == 2:
                syear = temp_rs[0].ayear
                smonth = temp_rs[0].amonth
                if smonth == "1":
                    pre_month = "12"
                    pre_year = temp_rs[0].ayear - 1
                else:
                    pre_year = temp_rs[1].ayear
                    pre_month = temp_rs[1].amonth
            else:
                syear = temp_rs[0].ayear
                smonth = temp_rs[0].amonth
                pre_year = temp_rs[0].ayear
                pre_month = temp_rs[0].amonth
        else:
            # If no records exist, use the current year and month as fallback
            syear = date.today().year
            smonth = str(date.today().month).zfill(2)  # Ensuring month is two digits

    else:
        # If syear and smonth are provided, ensure proper formatting
        syear = str(syear)
        smonth = str(smonth)
        if smonth == "1":
            pre_month = "12"
            pre_year = temp_rs[0].ayear - 1
        else:
            pre_year = temp_rs[0].ayear
            pre_month = temp_rs[0].amonth

    # rs = ReportMasterStat.objects.all()
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth)
    rs_pre = ReportMasterStat.objects.filter(ayear=pre_year, amonth=pre_month)

    # 휴먼영상만 가져오기
    rs_human = (
        rs.filter(company=1)
        .values("amodality")
        .annotate(t_count=Sum("total_count"), t_revenue=Sum("total_revenue"))
        .order_by("amodality")
    )

    # 병원수 구하기
    cm = (
        rs.values("company_id")  # Group by company_id
        .annotate(company_count=Count("company"))  # Count occurrences of each company
        .order_by("company_id")  # Order by company ID
    )
    cm_total = cm.count()

    # 닥터수 구하기
    dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    dr_total = dr.count()

    # 의뢰수 구하기
    rp_total = ReportMaster.objects.filter(ayear=syear, amonth=smonth).aggregate(
        report_count=Count("id")
    )
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs.aggregate(revenue_sum=Sum("total_revenue"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs.values("amodality")
        .annotate(
            amodality_count=Sum("total_count"),  # Summing total_count per modality
            amodality_total=Sum("total_revenue"),
        )
        .order_by("-amodality_total")
    )

    # 병원별 통계
    rs_cm = (
        rs.values("company__business_name")
        .annotate(
            company_count=Sum("total_count"),  # Summing total_count per modality
            company_total=Sum("total_revenue"),
        )
        .order_by("-company_total")[0:10]
    )
    # 판독의별 통계
    rs_dr = (
        rs.values("provider__profile__real_name")
        .annotate(
            provider_count=Sum("total_count"),  # Summing total_count per modality
            provider_total=Sum("total_revenue"),
        )
        .order_by("-provider_total")[0:10]
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth)
    # rs_ct_time = rs_graph.filter(amodality="CT")
    # rs_ct_time_1hr = rs_ct_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_ct_time_3hr = rs_ct_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_ct_time_1d = rs_ct_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_ct_time_3d = rs_ct_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_ct_time_7d = rs_ct_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_ct_time_more = rs_ct_time.filter(time_to_complete__gt=10080).count()

    # rs_mr_time = rs_graph.filter(amodality="MR")
    # rs_mr_time_1hr = rs_mr_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_mr_time_3hr = rs_mr_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_mr_time_1d = rs_mr_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_mr_time_3d = rs_mr_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_mr_time_7d = rs_mr_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_mr_time_more = rs_mr_time.filter(time_to_complete__gt=10080).count()

    # rs_cr_time = rs_graph.filter(amodality="CR")
    # rs_cr_time_1hr = rs_cr_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_cr_time_3hr = rs_cr_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_cr_time_1d = rs_cr_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_cr_time_3d = rs_cr_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_cr_time_7d = rs_cr_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_cr_time_more = rs_cr_time.filter(time_to_complete__gt=10080).count()

    # rs_time_dataset_ct = [
    #     rs_ct_time_1hr,
    #     rs_ct_time_3hr,
    #     rs_ct_time_1d,
    #     rs_ct_time_3d,
    #     rs_ct_time_7d,
    #     rs_ct_time_more,
    # ]
    # rs_time_dataset_mr = [
    #     rs_mr_time_1hr,
    #     rs_mr_time_3hr,
    #     rs_mr_time_1d,
    #     rs_mr_time_3d,
    #     rs_mr_time_7d,
    #     rs_mr_time_more,
    # ]
    # rs_time_dataset_cr = [
    #     rs_cr_time_1hr,
    #     rs_cr_time_3hr,
    #     rs_cr_time_1d,
    #     rs_cr_time_3d,
    #     rs_cr_time_7d,
    #     rs_cr_time_more,
    # ]

    # 요일별 통계
    rs_weekday = (
        rs_graph.annotate(
            weekday=ExtractWeekDay(
                "requestdt"
            )  # Extracts the weekday from the DateTimeField
        )
        .values("weekday")
        .annotate(weekday_total_count=Count("id"))  # Counts rows for each weekday
        .order_by("weekday")
    )

    context = {
        "cm_total": cm_total,
        "dr_total": dr_total,
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "rs_dr": rs_dr,
        "buttons_year_month": buttons_year_month,
        # "rs_time_dataset_ct": rs_time_dataset_ct,
        # "rs_time_dataset_mr": rs_time_dataset_mr,
        # "rs_time_dataset_cr": rs_time_dataset_cr,
        "rs_weekday": rs_weekday,
    }

    return render(request, "briefing/index.html", context)


def partial_briefing(request):
    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        # Fetch the latest available record from the database
        temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth").first()

        # Check if any records exist in the database
        if temp_rs:
            syear = temp_rs.ayear
            smonth = temp_rs.amonth

        else:
            # If no records exist, use the current year and month as fallback
            syear = date.today().year
            smonth = str(date.today().month).zfill(2)  # Ensuring month is two digits

    else:
        # If syear and smonth are provided, ensure proper formatting
        syear = str(syear)
        smonth = str(smonth)

    # rs = ReportMasterStat.objects.all()
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth)

    # 휴먼영상만 가져오기
    rs_human = (
        rs.filter(company=1)
        .values("amodality")
        .annotate(t_count=Sum("total_count"), t_revenue=Sum("total_revenue"))
        .order_by("amodality")
    )

    # 병원수 구하기
    cm = (
        rs.values("company_id")  # Group by company_id
        .annotate(company_count=Count("company"))  # Count occurrences of each company
        .order_by("company_id")  # Order by company ID
    )
    cm_total = cm.count()

    # 닥터수 구하기
    dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    dr_total = dr.count()

    # 의뢰수 구하기
    #   rp_total = rs.aggregate(report_count=Sum("total_count"))
    rp_total = ReportMaster.objects.filter(ayear=syear, amonth=smonth).aggregate(
        report_count=Count("id")
    )
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs.aggregate(revenue_sum=Sum("total_revenue"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs.values("amodality")
        .annotate(
            amodality_count=Sum("total_count"),  # Summing total_count per modality
            amodality_total=Sum(
                "total_revenue"
            ),  # Correcting field name to total_revenue
        )
        .order_by("-amodality_total")
    )

    # 병원별 통계
    rs_cm = (
        rs.values("company__business_name")
        .annotate(
            company_count=Sum("total_count"),  # Summing total_count per modality
            company_total=Sum("total_revenue"),
        )
        .order_by("-company_total")[0:10]
    )
    # 판독의별 통계
    rs_dr = (
        rs.values("provider__profile__real_name")
        .annotate(
            provider_count=Sum("total_count"),  # Summing total_count per modality
            provider_total=Sum("total_revenue"),
        )
        .order_by("-provider_total")[0:10]
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth)
    # rs_ct_time = rs_graph.filter(amodality="CT")
    # rs_ct_time_1hr = rs_ct_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_ct_time_3hr = rs_ct_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_ct_time_1d = rs_ct_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_ct_time_3d = rs_ct_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_ct_time_7d = rs_ct_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_ct_time_more = rs_ct_time.filter(time_to_complete__gt=10080).count()

    # rs_mr_time = rs_graph.filter(amodality="MR")
    # rs_mr_time_1hr = rs_mr_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_mr_time_3hr = rs_mr_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_mr_time_1d = rs_mr_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_mr_time_3d = rs_mr_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_mr_time_7d = rs_mr_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_mr_time_more = rs_mr_time.filter(time_to_complete__gt=10080).count()

    # rs_cr_time = rs_graph.filter(amodality="CR")
    # rs_cr_time_1hr = rs_cr_time.filter(
    #     time_to_complete__gte=1, time_to_complete__lte=60
    # ).count()
    # rs_cr_time_3hr = rs_cr_time.filter(
    #     time_to_complete__gt=60, time_to_complete__lte=180
    # ).count()
    # rs_cr_time_1d = rs_cr_time.filter(
    #     time_to_complete__gt=180, time_to_complete__lte=1440
    # ).count()
    # rs_cr_time_3d = rs_cr_time.filter(
    #     time_to_complete__gt=1440, time_to_complete__lte=4320
    # ).count()
    # rs_cr_time_7d = rs_cr_time.filter(
    #     time_to_complete__gt=4320, time_to_complete__lte=10080
    # ).count()
    # rs_cr_time_more = rs_cr_time.filter(time_to_complete__gt=10080).count()

    # rs_time_dataset_ct = [
    #     rs_ct_time_1hr,
    #     rs_ct_time_3hr,
    #     rs_ct_time_1d,
    #     rs_ct_time_3d,
    #     rs_ct_time_7d,
    #     rs_ct_time_more,
    # ]
    # rs_time_dataset_mr = [
    #     rs_mr_time_1hr,
    #     rs_mr_time_3hr,
    #     rs_mr_time_1d,
    #     rs_mr_time_3d,
    #     rs_mr_time_7d,
    #     rs_mr_time_more,
    # ]
    # rs_time_dataset_cr = [
    #     rs_cr_time_1hr,
    #     rs_cr_time_3hr,
    #     rs_cr_time_1d,
    #     rs_cr_time_3d,
    #     rs_cr_time_7d,
    #     rs_cr_time_more,
    # ]

    # 요일별 통계
    rs_weekday = (
        rs_graph.annotate(
            weekday=ExtractWeekDay(
                "requestdt"
            )  # Extracts the weekday from the DateTimeField
        )
        .values("weekday")
        .annotate(weekday_total_count=Count("id"))  # Counts rows for each weekday
        .order_by("weekday")
    )

    context = {
        "cm_total": cm_total,
        "dr_total": dr_total,
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "rs_dr": rs_dr,
        "buttons_year_month": buttons_year_month,
        # "rs_time_dataset_ct": rs_time_dataset_ct,
        # "rs_time_dataset_mr": rs_time_dataset_mr,
        # "rs_time_dataset_cr": rs_time_dataset_cr,
        "rs_weekday": rs_weekday,
    }

    return render(request, "briefing/partial_briefing.html", context)
