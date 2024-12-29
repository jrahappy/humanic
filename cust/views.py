# Create your views here.
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import ExtractWeekDay
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from minibooks.models import ReportMaster, ReportMasterStat, UploadHistory, MagamMaster
from accounts.forms import ProfileForm
from customer.models import Company
from allauth.account.forms import ChangePasswordForm
import csv


@login_required
def password_change(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            update_session_auth_hash(request, form.user)
            return HttpResponse(
                '<script>window.location.href="%s";</script>'
                % reverse_lazy("dashboard:password_change_done")
            )  # Redirect to success URL using JavaScript if the form is valid

        else:
            messages.error(request, "There was an error in your password update.")
            return render(request, "dashboard/password_change.html", {"form": form})
    else:
        form = ChangePasswordForm(user=request.user)

    context = {
        "form": form,
    }

    return render(request, "dashboard/password_change.html", context)


def password_change_done(request):
    return render(request, "dashboard/password_change_done.html")


@login_required
def edit_profile(request):
    user = request.user
    form = ProfileForm(instance=user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        # print(form)
        if form.is_valid():
            # user = request.user
            form.save()
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["real_name"]
            user.save()

            messages.success(request, "Profile updated.")
            return redirect("dashboard:profile")
        else:
            messages.error(request, "There was an error in your profile update.")
            print(form.errors)
            # Display errors in the console    else:
        form = ProfileForm(instance=user.profile)

    return render(request, "dashboard/edit_profile.html", {"form": form})


@login_required
def index(request):
    user = request.user

    # 연결되어 있는 병원 정보를 가져온다.
    company = Company.objects.filter(customuser=user).first()
    if not company:
        messages.error(request, "Error 301번: 연결된 병원 정보가 없습니다.")
        user.logout()
        return redirect("account_login")
    else:
        # 협진병원의 경우 collab 페이지로 이동
        if company.is_collab:
            return redirect("collab:index")

    # Check if the user is a staff member
    if user.is_staff:
        return redirect("briefing:index")

    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        recent_rs = (
            MagamMaster.objects.filter(is_opened=True)
            .order_by("-ayear", "-amonth")
            .first()
        )
        if recent_rs:
            syear = recent_rs.ayear
            smonth = recent_rs.amonth
        else:
            syear = date.today().year
            smonth = str(date.today().month).zfill(2)
    else:
        syear = str(syear)
        smonth = str(smonth)

    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth, company=company)
    rs_money = ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)

    # 병원수 구하기
    cm = (
        rs.values("provider_id")  # Group by provider_id
        .annotate(company_count=Count("provider"))  # Count occurrences of each company
        .order_by("provider_id")  # Order by company ID
    )
    cm_total = cm.count()

    # # 닥터수 구하기
    # dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    # dr_total = dr.count()

    # 의뢰수 구하기
    rp_total = ReportMaster.objects.filter(
        ayear=syear, amonth=smonth, company=company
    ).aggregate(report_count=Count("id"))
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs_money.aggregate(revenue_sum=Sum("readprice"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs_money.values("amodality")
        .annotate(
            amodality_count=Count("id"),  # Summing total_count per modality
            amodality_total=Sum("readprice"),
        )
        .order_by("-amodality_total")
    )

    # 판독의별 통계
    rs_cm = (
        rs_money.values("provider__profile__real_name")
        .annotate(
            company_count=Count("id"),  # Summing total_count per modality
            company_total=Sum("readprice"),
        )
        .order_by("-company_total")
    )

    # 월단위 버튼 만들기
    buttons_year_month = (
        MagamMaster.objects.filter(is_opened=True)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    # 그래프용 데이터
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)
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
        # "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "buttons_year_month": buttons_year_month,
        "rs_weekday": rs_weekday,
        "side_menu": "dashboard",
        "company": company,
    }

    return render(request, "cust/index.html", context)


def partial_dashboard(request):
    user = request.user

    # 연결되어 있는 병원 정보를 가져온다.
    company = Company.objects.filter(customuser=user).first()

    # Check if the user is a staff member
    if user.is_staff:
        return redirect("briefing:index")

    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    if not syear or not smonth:
        recent_rs = (
            MagamMaster.objects.filter(is_opened=True)
            .order_by("-ayear", "-amonth")
            .first()
        )
        if recent_rs:
            syear = recent_rs.ayear
            smonth = recent_rs.amonth
        else:
            syear = date.today().year
            smonth = str(date.today().month).zfill(2)
    else:
        syear = str(syear)
        smonth = str(smonth)

    # if not syear or not smonth:
    #     # Fetch the latest available record from the database
    #     # temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth").first()
    #     # 월단위 버튼 만들기

    #     temp_rs = ReportMasterStat.objects.all().order_by("-ayear", "-amonth")[:2]
    #     # Check if any records exist in the database
    #     if temp_rs:
    #         if temp_rs.count() == 2:
    #             syear = temp_rs[0].ayear
    #             smonth = temp_rs[0].amonth
    #             if smonth == "1":
    #                 pre_month = "12"
    #                 pre_year = temp_rs[0].ayear - 1
    #             else:
    #                 pre_year = temp_rs[1].ayear
    #                 pre_month = temp_rs[1].amonth
    #         else:
    #             syear = temp_rs[0].ayear
    #             smonth = temp_rs[0].amonth
    #             pre_year = temp_rs[0].ayear
    #             pre_month = temp_rs[0].amonth
    #     else:
    #         # If no records exist, use the current year and month as fallback
    #         syear = date.today().year
    #         smonth = str(date.today().month).zfill(2)  # Ensuring month is two digits

    # else:
    #     # If syear and smonth are provided, ensure proper formatting
    #     syear = str(syear)
    #     smonth = str(smonth)

    # rs = ReportMasterStat.objects.all()
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth, company=company)
    rs_money = ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)
    # rs_pre = ReportMasterStat.objects.filter(
    #     ayear=pre_year, amonth=pre_month, company=company
    # )

    # 휴먼영상만 가져오기
    # rs_human = (
    #     rs.filter(company=1)
    #     .values("amodality")
    #     .annotate(t_count=Sum("total_count"), t_revenue=Sum("total_revenue"))
    #     .order_by("amodality")
    # )

    # 병원수 구하기
    cm = (
        rs.values("provider_id")  # Group by provider_id
        .annotate(company_count=Count("provider"))  # Count occurrences of each company
        .order_by("provider_id")  # Order by company ID
    )
    cm_total = cm.count()

    # # 닥터수 구하기
    # dr = rs.values("provider").annotate(doctor_total=Count("provider"))
    # dr_total = dr.count()

    # 의뢰수 구하기
    rp_total = ReportMaster.objects.filter(
        ayear=syear, amonth=smonth, company=company
    ).aggregate(report_count=Count("id"))
    rp_total_value = rp_total["report_count"] or 0

    # 응급의뢰수 구하기 (Get the count of emergency reports)
    rp_er_total = rs.filter(emergency=True).aggregate(report_count=Sum("total_count"))
    rp_er_total_value = rp_er_total["report_count"] or 0

    # 매출 구하기
    revenue_total = rs_money.aggregate(revenue_sum=Sum("readprice"))
    revenue_total_value = revenue_total["revenue_sum"] or 0

    # 모달러티별 통계
    rs_modality = (
        rs_money.values("amodality")
        .annotate(
            amodality_count=Count("id"),  # Summing total_count per modality
            amodality_total=Sum("readprice"),
        )
        .order_by("-amodality_total")
    )

    # 판독의별 통계
    rs_cm = (
        rs_money.values("provider__profile__real_name")
        .annotate(
            company_count=Count("id"),  # Summing total_count per modality
            company_total=Sum("readprice"),
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
    rs_graph = ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)
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
        # "rs_human": rs_human,
        "syear": syear,
        "smonth": smonth,
        "rs_modality": rs_modality,
        "rs_cm": rs_cm,
        "buttons_year_month": buttons_year_month,
        "rs_weekday": rs_weekday,
        "side_menu": "dashboard",
        "company": company,
    }

    return render(request, "cust/partial_dashboard.html", context)


def profile(request):
    user = request.user
    form = ProfileForm(instance=user.profile)

    return render(request, "dashboard/profile.html", {"form": form})


def user_logout(request):
    return render(request, "dashboard/logout.html")


def stat(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()

    # 월단위 버튼 만들기
    buttons_year_month = (
        MagamMaster.objects.filter(is_opened=True)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-ayear", "-amonth")
    )

    context = {
        "buttons_year_month": buttons_year_month,
        "radio": user,
        "side_menu": "stat",
        "company": company,
    }
    return render(request, "cust/stat.html", context)


def report_period_month_company(request, ayear, amonth, company_id):
    company = Company.objects.filter(id=company_id).first()
    # 병원 정보가 없으면 에러 메시지 출력
    if not company:
        messages.error(request, "Error 301번: 연결된 병원 정보가 없습니다.")
        return redirect("cust:index")

    rpms = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=company)
        .values(
            # "platform",
            "provider__profile__real_name",
            "amodality",
            "is_onsite",
        )
        .annotate(
            r_total_price=Sum("readprice"),
            r_total_cases=Count("case_id"),
        )
        .order_by("provider__profile__real_name", "amodality")
    )
    count_rpms = rpms.count()

    # 일반 판독금액 합계
    total_by_onsite = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=company)
        .values("is_take")
        .annotate(
            total_price=Sum("readprice"),
            total_cases=Count("case_id"),
        )
        .order_by("is_onsite")
    )

    total_by_amodality = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=company)
        .values("amodality")
        .annotate(
            total_price=Sum("readprice"),
            total_cases=Count("case_id"),
        )
        .order_by("amodality")
    )

    providers = (
        ReportMaster.objects.filter(ayear=ayear, amonth=amonth, company=company)
        .values("provider__profile__real_name")
        .distinct()
    )

    count_providers = providers.count()

    context = {
        "company": company,
        "company_id": company_id,
        "rpms": rpms,
        "count_rpms": count_rpms,
        "count_providers": count_providers,
        "ayear": ayear,
        "amonth": amonth,
        "providers": providers,
        "total_by_onsite": total_by_onsite,
        "total_by_amodality": total_by_amodality,
    }

    return render(request, "cust/report_period_month_company.html", context)


def report_period_month_company_detail(
    request, ayear, amonth, provider, company, amodality
):

    rpms = ReportMaster.objects.filter(
        ayear=ayear,
        amonth=amonth,
        provider__profile__real_name=provider,
        company=company,
        amodality=amodality,
    ).order_by("case_id")[:1000]
    count_rpms = rpms.count()
    # s_provider = CustomUser.objects.get(id=radio)
    # print(provider)
    # provider = CustomUser.objects.get(id=provider)
    # print("new provider:", provider.id)
    company = Company.objects.get(id=company)
    context = {
        "rpms": rpms,
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "provider": provider,
        "company": company,
        "amodality": amodality,
    }

    return render(request, "cust/report_period_month_company_detail.html", context)


def export_csv(request, ayear, amonth, company_id):

    company = Company.objects.filter(id=company_id).first()

    rpms = ReportMaster.objects.filter(
        ayear=ayear, amonth=amonth, company=company
    ).order_by("case_id")
    count_rpms = rpms.count()
    file_name = f"{ayear}_{amonth}_{company.business_name}.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'

    writer = csv.writer(response)
    for rpm in rpms:
        writer.writerow(
            [
                rpm.case_id,
                rpm.name,
                rpm.department,
                rpm.bodypart,
                rpm.amodality,
                rpm.readprice,
                rpm.provider.profile.real_name,
                rpm.requestdt,
                rpm.approvedt,
            ]
        )

    return response
