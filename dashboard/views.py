# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import ExtractWeekDay
from django.contrib.auth.decorators import login_required
from minibooks.models import ReportMaster, ReportMasterStat, UploadHistory
from accounts.forms import ProfileForm
from accounts.models import CustomUser, Profile


@login_required
def index(request):
    user = request.user
    # Check if the user is a staff member
    if user.is_staff:
        return redirect("brief:index")

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
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth, provider=user)
    rs_money = ReportMaster.objects.filter(ayear=syear, amonth=smonth, provider=user)
    # rs_pre = ReportMasterStat.objects.filter(
    #     ayear=pre_year, amonth=pre_month, provider=user
    # )

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

    # # 닥터수 구하기
    # dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    # dr_total = dr.count()

    # 의뢰수 구하기
    rp_total = ReportMaster.objects.filter(
        ayear=syear, amonth=smonth, provider=user
    ).aggregate(report_count=Count("id"))
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs_money.aggregate(revenue_sum=Sum("pay_to_provider"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs_money.values("amodality")
        .annotate(
            amodality_count=Count("id"),  # Summing total_count per modality
            amodality_total=Sum("pay_to_provider"),
        )
        .order_by("-amodality_total")
    )

    # 병원별 통계
    rs_cm = (
        rs_money.values("company__business_name")
        .annotate(
            company_count=Count("id"),  # Summing total_count per modality
            company_total=Sum("pay_to_provider"),
        )
        .order_by("-company_total")
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth, provider=user)
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
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "buttons_year_month": buttons_year_month,
        "rs_weekday": rs_weekday,
        "side_menu": "dashboard",
    }

    return render(request, "dashboard/index.html", context)


def partial_dashboard(request):
    user = request.user
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
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth, provider=user)
    rs_money = ReportMaster.objects.filter(ayear=syear, amonth=smonth, provider=user)
    # rs_pre = ReportMasterStat.objects.filter(
    #     ayear=pre_year, amonth=pre_month, provider=user
    # )

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

    # # 닥터수 구하기
    # dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    # dr_total = dr.count()

    # 의뢰수 구하기
    rp_total = ReportMaster.objects.filter(
        ayear=syear, amonth=smonth, provider=user
    ).aggregate(report_count=Count("id"))
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs_money.aggregate(revenue_sum=Sum("pay_to_provider"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs_money.values("amodality")
        .annotate(
            amodality_count=Count("id"),  # Summing total_count per modality
            amodality_total=Sum("pay_to_provider"),
        )
        .order_by("-amodality_total")
    )

    # 병원별 통계
    rs_cm = (
        rs_money.values("company__business_name")
        .annotate(
            company_count=Count("id"),  # Summing total_count per modality
            company_total=Sum("pay_to_provider"),
        )
        .order_by("-company_total")
    )

    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth, provider=user)
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
        "rp_total": rp_total_value,
        "rp_er_total_value": rp_er_total_value,
        "revenue_total": revenue_total_value,
        "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "buttons_year_month": buttons_year_month,
        "rs_weekday": rs_weekday,
        "side_menu": "dashboard",
    }

    return render(request, "dashboard/partial_dashboard.html", context)


def profile(request):
    user = request.user

    form = ProfileForm(instance=user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user.profile)

    return render(request, "dashboard/profile.html", {"form": form})


def user_logout(request):
    return render(request, "dashboard/logout.html")


def stat(request):
    user = request.user
    buttons_year_month = (
        UploadHistory.objects.filter(is_deleted=False)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {
        "buttons_year_month": buttons_year_month,
        "radio": user,
        "side_menu": "stat",
    }
    return render(request, "dashboard/stat.html", context)


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

    return render(request, "dashboard/report_period_month_radiologist.html", context)


def daisyui(request):
    return render(request, "dashboard/daisyui.html")
