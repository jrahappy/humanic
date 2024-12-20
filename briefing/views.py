from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.db.models.functions import ExtractWeekDay

# from importdata.models import rawdata, UploadHistory
from minibooks.models import UploadHistory, ReportMaster, ReportMasterStat
from accounts.models import Profile, CustomUser
from django.contrib.auth.decorators import login_required
from datetime import date


@login_required
def index(request):
    user = request.user
    # Check if the user is a staff member
    if user.is_staff:
        pass
    else:
        # 판독의의 경우
        if user.is_doctor:
            return redirect("dashboard:index")
        # 병원(고객)의 경우
        else:
            return redirect("cust:index")

    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        # Fetch the latest available record from the database
        # temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth").first()
        # temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth")[:2]
        temp_rs = UploadHistory.objects.filter(is_deleted=False).order_by("-id")[:1]
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

    print(syear, smonth)

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
    buttons_year_month = sorted(
        buttons_year_month,
        key=lambda x: (int(x["ayear"]), int(x["amonth"])),
        reverse=True,
    )

    # 전체 통계
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth)
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

    # 닥터의 스페셜티별 통계
    dr_by_specialty = (
        rs.values("provider__profile__specialty2")
        .annotate(
            provider_count=Count("provider", distinct=True),
            sum_total_revenue=Sum("total_revenue"),
            avg_total_revenue=Sum("total_revenue") / Count("provider", distinct=True),
        )  # Ensure distinct provider count per specialty
        .order_by("-provider_count")
    )

    # print(dr_by_specialty)

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
        "rs_weekday": rs_weekday,
        "dr_by_specialty": dr_by_specialty,
    }

    return render(request, "briefing/index.html", context)


def partial_briefing(request):
    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        # Fetch the latest available record from the database
        # temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth").first()
        temp_rs = UploadHistory.objects.filter(is_deleted=False).order_by(
            "-created_at"
        )[:1]

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

    print(syear, smonth)

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

    # 닥터의 스페셜티별 통계
    dr_by_specialty = (
        rs.values("provider__profile__specialty2")
        .annotate(
            provider_count=Count("provider", distinct=True),
            sum_total_revenue=Sum("total_revenue"),
            avg_total_revenue=Sum("total_revenue") / Count("provider", distinct=True),
        )  # Ensure distinct provider count per specialty
        .order_by("-provider_count")
    )

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
        .order_by("-ayear", "amonth")
    )

    # print(buttons_year_month)

    buttons_year_month = sorted(
        buttons_year_month,
        key=lambda x: (int(x["ayear"]), int(x["amonth"])),
        reverse=True,
    )

    # for buttons
    # print(buttons_year_month)

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth)

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

    # rs_fixtures = CustomUser.objects.filter(is_doctor=True)
    # rs_fixtures = (
    #     Profile.objects.filter(
    #         user__is_doctor=True,
    #         user__is_active=True,
    #         contract_status="A",
    #         user__reportmasterstat__ayear=syear,
    #         user__reportmasterstat__amonth=smonth,
    #     ).exclude(specialty2=None)
    #     # .exclude(contract_status="T")
    # )

    # dr_by_specialty = (
    #     rs_fixtures.values("specialty2")
    #     .annotate(provider_count=Count("specialty2"))
    #     .order_by("-provider_count")
    # )

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
        "dr_by_specialty": dr_by_specialty,
    }

    return render(request, "briefing/partial_briefing.html", context)
