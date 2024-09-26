from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Avg
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
    if not user.is_staff:
        return redirect("dashboard:index")

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
        .order_by("-company_total")[0:15]
    )
    # 판독의별 통계
    rs_dr = (
        rs.values("provider__profile__real_name")
        .annotate(
            provider_count=Sum("total_count"),  # Summing total_count per modality
            provider_total=Sum("total_revenue"),
        )
        .order_by("-provider_total")[0:15]
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {
        "cm_total": cm_total,
        "dr_total": dr_total,
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "rs_dr": rs_dr,
        "buttons_year_month": buttons_year_month,
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
    # rp_total = rs.aggregate(report_count=Sum("total_count"))
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
        .order_by("-company_total")[0:15]
    )
    # 판독의별 통계
    rs_dr = (
        rs.values("provider__profile__real_name")
        .annotate(
            provider_count=Sum("total_count"),  # Summing total_count per modality
            provider_total=Sum("total_revenue"),
        )
        .order_by("-provider_total")[0:15]
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {
        "cm_total": cm_total,
        "dr_total": dr_total,
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "rs_dr": rs_dr,
        "buttons_year_month": buttons_year_month,
    }

    return render(request, "briefing/partial_briefing.html", context)
