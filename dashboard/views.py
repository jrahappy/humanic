# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.db.models.functions import ExtractWeekDay
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from minibooks.models import ReportMaster, ReportMasterStat, UploadHistory, MagamMaster
from accounts.forms import ProfileForm
from accounts.models import CustomUser, Profile, WorkHours, Holidays, ProductionTarget
from blog.models import Post, PostAttachment
from allauth.account.forms import ChangePasswordForm
from django.core.paginator import Paginator
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime, timedelta, date
from utils.base_func import (
    get_amodality_choices,
    APPT_DAYS,
    HOLIDAY_CATEGORY,
    TERM_CATEGORY,
    WORKHOURS,
)
from .forms import ProductionTargetForm
import json


def create_weekday_modality_target(request, id):
    user = request.user
    provider = CustomUser.objects.get(id=id)
    real_name = provider.profile.real_name
    # week_days = APPT_DAYS
    # amodality = get_amodality_choices()
    if request.method == "POST":
        form = ProductionTargetForm(request.POST)
        # 요일 정보를 리스트로 받기
        work_weekdays = request.POST.getlist("work_weekday")
        # .get("work_weekday")
        # print(work_weekdays)
        modality = form.data.get("modality")

        i = 0
        for ww in work_weekdays:
            # print("weekday", i, ":", ww)
            # 기존 타겟이 있는지 확인

            is_exist = ProductionTarget.objects.filter(
                user=provider, work_weekday=ww, modality=modality
            ).exists()

            # 타겟이 있으면 업데이트
            if is_exist:

                if form.is_valid():
                    target_v = form.cleaned_data.get("target_value")
                    max_v = form.cleaned_data.get("max_value")

                    target = ProductionTarget.objects.get(
                        user=provider, work_weekday=ww, modality=modality
                    )
                    target.target_value = target_v
                    target.max_value = max_v
                    target.save()
                # return HttpResponse(
                #     status=204,
                #     headers={
                #         "HX-Trigger": json.dumps(
                #             {
                #                 "targetListChanged": None,
                #                 "showMessage": "Target updated successfully.",
                #             }
                #         )
                #     },
                # )

            # 타겟이 없으면 생성
            else:

                if form.is_valid():
                    target = ProductionTarget.objects.create(
                        user=provider,
                        work_weekday=ww,
                        modality=modality,
                        target_value=form.cleaned_data["target_value"],
                        max_value=form.cleaned_data["max_value"],
                    )

                    # tg = form.save(commit=False)
                    # tg.user = provider
                    # tg.work_weekday = ww
                    # tg.modality = modality
                    # tg.save()
                    # return HttpResponse(
                    #     status=204,
                    #     headers={
                    #         "HX-Trigger": json.dumps(
                    #             {
                    #                 "targetListChanged": None,
                    #                 "showMessage": "Target created successfully.",
                    #             }
                    #         )
                    #     },
                    # )
                else:
                    print(form.errors)
                    return render(
                        request,
                        "dashboard/partial/work_weekday_modality.html",
                        {
                            "form": form,
                            "real_name": real_name,
                        },
                    )

        return HttpResponse(
            status=204,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "targetListChanged": None,
                        "showMessage": "Target updated successfully.",
                    }
                )
            },
        )
    else:
        form = ProductionTargetForm()

    context = {
        "real_name": real_name,
        "form": form,
    }

    return render(request, "dashboard/week_day_modality.html", context)


# def create_weekday_modality_target(request, id):
#     provider = get_object_or_404(CustomUser, id=id)
#     real_name = provider.profile.real_name

#     if request.method == "POST":
#         form = ProductionTargetForm(request.POST)
#         if form.is_valid():
#             work_weekdays = form.cleaned_data.get("work_weekday")
#             modality = form.cleaned_data.get("modality")
#             target_value = form.cleaned_data.get("target_value")
#             max_value = form.cleaned_data.get("max_value")

#             # Retrieve existing targets for the provider and modality
#             existing_targets = ProductionTarget.objects.filter(
#                 user=provider, modality=modality, work_weekday__in=work_weekdays
#             )

#             existing_weekdays = set(
#                 existing_targets.values_list("work_weekday", flat=True)
#             )

#             # Update existing targets
#             for target in existing_targets:
#                 target.target_value = target_value
#                 target.max_value = max_value
#                 target.save()

#             # Create new targets for weekdays without existing entries
#             new_weekdays = set(work_weekdays) - existing_weekdays
#             ProductionTarget.objects.bulk_create(
#                 [
#                     ProductionTarget(
#                         user=provider,
#                         work_weekday=weekday,
#                         modality=modality,
#                         target_value=target_value,
#                         max_value=max_value,
#                     )
#                     for weekday in new_weekdays
#                 ]
#             )

#             return HttpResponse(
#                 status=204,
#                 headers={
#                     "HX-Trigger": json.dumps(
#                         {
#                             "targetListChanged": None,
#                             "showMessage": "Targets updated successfully.",
#                         }
#                     )
#                 },
#             )
#         else:
#             # If the form is invalid, render the form with errors
#             return render(
#                 request,
#                 "dashboard/partial/work_weekday_modality.html",
#                 {
#                     "form": form,
#                     "real_name": real_name,
#                 },
#             )
#     else:
#         form = ProductionTargetForm(request.POST)
#         return render(
#             request,
#             "dashboard/partial/work_weekday_modality.html",
#             {
#                 "form": form,
#                 "real_name": real_name,
#             },
#         )


# 타겟 목록 보여주기(Partial)
def weekday_modality_targets(request, id):
    provider = CustomUser.objects.get(id=id)
    wm_targets = ProductionTarget.objects.filter(user=id).order_by(
        "work_weekday", "modality"
    )
    # print(wm_targets.count())

    context = {
        "provider": provider,
        "week_days": APPT_DAYS,
        "targets": wm_targets,
    }

    return render(request, "dashboard/partial/weekday_modality_targets.html", context)


def delete_weekday_modality_target(request, id):
    target = ProductionTarget.objects.get(id=id)
    target.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "targetListChanged": None,
                    "showMessage": "Target deleted successfully.",
                }
            )
        },
    )


def get_year_calendar(year):
    months = []
    today = timezone.now().date()
    current_month = int(today.month)
    # 향후 3개월 달력만 보여주기
    current_12_months = range(current_month, current_month + 3)
    # print(current_12_months)
    flag_year = False
    for month in current_12_months:
        if month > 12:
            month -= 12
            if not flag_year:
                year += 1
                flag_year = True

        month_days = []
        _, num_days = calendar.monthrange(year, month)
        start_day = calendar.monthrange(year, month)[0]

        # Create padding for the start of the month
        start_day_padding = [""] * start_day

        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            month_days.append({"day": day, "date": date, "is_today": date == today})

        months.append(
            {
                "name": calendar.month_name[month],
                "start_day_padding": start_day_padding,
                "days": month_days,
            }
        )
    return months


# 한달 달력 만들기 (해당 월만 업데이트하기 위해서 만듬)
def get_month_calendar(year, month):
    # Get today's date
    today = timezone.now().date()

    # Initialize the list for the current month
    amonth = []

    # Get the number of days and the starting weekday for the month
    _, num_days = calendar.monthrange(year, month)
    start_day = calendar.monthrange(year, month)[0]

    # Create padding for the start of the month
    start_day_padding = [""] * start_day

    # Collect day information
    month_days = []
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        month_days.append(
            {
                "day": day,
                "date": date,
                "is_today": date == today,
                "is_past": date < today,
            }
        )

    # Create the month structure with name and padding
    amonth.append(
        {
            "name": calendar.month_name[month],
            "start_day_padding": start_day_padding,
            "days": month_days,
        }
    )

    return amonth


# workhours 초기 화면 구성
def workhours(request):
    user = request.user
    # 요일별 근무시간
    selected_workhours = WorkHours.objects.filter(user=user).order_by("work_weekday")
    selected_workhours_dict = {
        item["work_weekday"]: item["work_hour"]
        for item in selected_workhours.values("work_weekday", "work_hour")
    }
    # 휴일 OFF 등록
    selected_holidays = Holidays.objects.filter(user=user)
    selected_holidays_dict = {
        item["holiday_category"]: item["holidays"]
        for item in selected_holidays.values("holiday_category", "holidays")
    }
    # print(selected_holidays_dict)
    week_days = APPT_DAYS
    workhours = WORKHOURS
    amodality = get_amodality_choices()
    # print(amodality)

    targets = ProductionTarget.objects.filter(user=user).order_by(
        "work_weekday", "modality"
    )

    year = datetime.now().year
    months = get_year_calendar(year)

    context = {
        "user": user,
        "provider": user,
        "week_days": week_days,
        "workhours": workhours,
        "selected_workhours_dict": selected_workhours_dict,
        "months": months,
        "today_date": date.today(),
        "selected_holidays_dict": selected_holidays_dict,
        "targets": targets,
    }

    return render(request, "dashboard/wh.html", context)


# 휴무일 추가(사용자별)
def holiday_create(request):
    user = request.user
    holiday_category = request.GET.get("category")
    holiday_category = "p"
    holiday_name = request.GET.get("name")
    holiday_name = "Personal"
    month_name = request.GET.get("month_name")
    # 선택된 날짜
    hdate = request.GET.get("hdate")
    month_number = hdate.split("-")[1]
    year_number = hdate.split("-")[0]
    week_days = APPT_DAYS

    is_holiday = Holidays.objects.filter(user=user).exists()

    if is_holiday:
        holiday = Holidays.objects.get(user=user)
        holidays = holiday.holidays if isinstance(holiday.holidays, list) else []
        if hdate not in holidays:
            holidays.append(hdate)
        holiday.holidays = holidays
        # print("max", max(holidays))
        holiday.save()
    else:
        holiday = Holidays()
        holiday.user = user
        holiday.holiday_category = holiday_category
        holiday.holiday_name = holiday_name
        hdate_list = [hdate]
        holiday.holidays = hdate_list
        holiday.save()

    selected_holidays = holiday.holidays
    amonth = get_month_calendar(int(year_number), int(month_number))
    # print(selected_holidays)
    # print(amonth)

    context = {
        "amonth": amonth,
        "week_days": week_days,
        "selected_holidays": selected_holidays,
        "today_date": date.today(),
    }

    return render(request, "dashboard/partial/month_calendar.html", context)


def holiday_remove(request):
    user = request.user
    month_name = request.GET.get("month_name")
    # 선택된 날짜
    hdate = request.GET.get("hdate")
    month_number = hdate.split("-")[1]
    year_number = hdate.split("-")[0]
    week_days = APPT_DAYS

    holiday = Holidays.objects.get(user=user)
    holidays = holiday.holidays if isinstance(holiday.holidays, list) else []
    if hdate in holidays:
        holidays.remove(hdate)
    holiday.holidays = holidays
    holiday.save()

    selected_holidays = holiday.holidays
    amonth = get_month_calendar(int(year_number), int(month_number))

    context = {
        "amonth": amonth,
        "week_days": week_days,
        "selected_holidays": selected_holidays,
        "today_date": date.today(),
    }

    return render(request, "dashboard/partial/month_calendar.html", context)


def workhour_create(request, id):
    user = request.user
    provider = CustomUser.objects.get(id=id)
    week_day = request.GET.get("day")
    work_hour = request.GET.get("hour")

    is_workhour = WorkHours.objects.filter(
        user=provider, work_weekday=week_day
    ).exists()

    if is_workhour:
        workhour = WorkHours.objects.get(user=provider, work_weekday=week_day)
        wh_list = workhour.work_hour if isinstance(workhour.work_hour, list) else []
        # All day 처리
        if work_hour == "99":
            wh_list = [work_hour]
        else:
            if "99" in wh_list:
                wh_list.remove("99")
            wh_list.append(work_hour)

        workhour.work_hour = wh_list
        workhour.save()
        # print("old")
    else:
        workhour = WorkHours()
        workhour.user = provider
        workhour.work_weekday = week_day
        wh_list = [work_hour]
        workhour.work_hour = wh_list
        workhour.save()
    # print(wh_list)
    selected_workhours = wh_list

    context = {
        "provider": provider,
        "week_day": week_day,
        "week_days": APPT_DAYS,
        "workhours": WORKHOURS,
        "selected_workhours": selected_workhours,
    }

    return render(request, "dashboard/partial/week_day_hours.html", context)


def workhour_remove(request, id):
    user = request.user
    provider = CustomUser.objects.get(id=id)
    week_day = request.GET.get("day")
    work_hour = request.GET.get("hour")

    workhour = WorkHours.objects.get(user=provider, work_weekday=week_day)
    wh_list = workhour.work_hour
    wh_list.remove(work_hour)
    if wh_list == []:
        workhour.delete()
    else:
        workhour.work_hour = wh_list
        workhour.save()
    # print("removed")
    selected_workhours = wh_list

    context = {
        "provider": provider,
        "week_day": week_day,
        "week_days": APPT_DAYS,
        "workhours": WORKHOURS,
        "selected_workhours": selected_workhours,
    }

    return render(request, "dashboard/partial/week_day_hours.html", context)


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
    # Check if the user is a staff member
    if user.is_staff:
        return redirect("briefing:index")

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

    # rs = ReportMasterStat.objects.all()
    rs = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth, provider=user)
    rs_money = ReportMaster.objects.filter(ayear=syear, amonth=smonth, provider=user)

    # Check if any records exist in the database
    rs_existed = rs.exists()

    # 년도별 그래프 자료
    if rs_existed:
        stat = ReportMaster.objects.filter(ayear=syear, provider=user)
        stat_agg_by_amodality = (
            stat.values("ayear", "amonth", "amodality")
            .annotate(total_revenue=Sum("pay_to_provider"))
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
    else:
        chart = None

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

    # 월단위 버튼 만들기
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

    # 공지사항
    posts = Post.objects.filter(is_public=True).order_by("-created_at")[:5]

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
        "chart": chart,
        "posts": posts,
    }

    return render(request, "dashboard/index.html", context)


@login_required
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

    rs_existed = rs.exists()

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

    # 년도별 그래프 자료
    if rs_existed:

        stat = ReportMaster.objects.filter(ayear=syear, provider=user)
        stat_agg_by_amodality = (
            stat.values("ayear", "amonth", "amodality")
            .annotate(total_revenue=Sum("pay_to_provider"))
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
            # width=800,  # Set the overall plot width in pixels
            # height=600,  # Set the overall plot height in pixels
        )

        # Convert the chart to HTML
        chart = fig.to_html()
    else:
        chart = None

    # 공지사항
    posts = Post.objects.filter(is_public=True).order_by("-created_at")[:5]

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
        "chart": chart,
        "posts": posts,
    }

    return render(request, "dashboard/partial_dashboard.html", context)


@login_required
def profile(request):
    user = request.user
    form = ProfileForm(instance=user.profile)

    return render(request, "dashboard/profile.html", {"form": form})


@login_required
def user_logout(request):
    return render(request, "dashboard/logout.html")


@login_required
def stat(request):
    user = request.user

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

    context = {
        "buttons_year_month": buttons_year_month,
        "radio": user,
        "side_menu": "stat",
    }
    return render(request, "dashboard/stat.html", context)


@login_required
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

    df = pd.DataFrame(rpms)
    if df.empty:
        pivot_html = None
    else:
        pivot = pd.pivot_table(
            df,
            index=["company__business_name"],
            columns=["amodality"],
            values=[
                "r_total_provider",
                "r_total_cases",
            ],
            aggfunc={
                "r_total_provider": "sum",
                "r_total_cases": "sum",
            },
            margins=True,
            margins_name="Total",
        )
        # Format the values
        pivot["r_total_provider"] = (
            pivot["r_total_provider"]
            .fillna(0)
            .astype(int)
            .map(lambda x: f"{x:,.0f}")  # Apply formatting
        )
        pivot["r_total_cases"] = (
            pivot["r_total_cases"].fillna(0).astype(int).map(lambda x: f"{x:,.0f}")
        )

        pivot_html = pivot.to_html(classes="table table-zebra table-sm table-hover")

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
        "count_rpms": count_rpms,
        "ayear": ayear,
        "amonth": amonth,
        "radio": radio,
        "companies": companies,
        "provider": provider,
        "total_by_onsite": total_by_onsite,
        "total_by_amodality": total_by_amodality,
        "pivot_html": pivot_html,
    }

    return render(request, "dashboard/report_period_month_radiologist.html", context)


@login_required
def report_period_month_radiologist_detail(
    request, ayear, amonth, provider, company, amodality
):

    rpms = ReportMaster.objects.filter(
        ayear=ayear,
        amonth=amonth,
        provider=provider,
        company__business_name=company,
        amodality=amodality,
    ).order_by("case_id")[:1000]
    count_rpms = rpms.count()
    # s_provider = CustomUser.objects.get(id=radio)
    # print(provider)
    provider = CustomUser.objects.get(id=provider)
    # print("new provider:", provider.id)
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
        request, "dashboard/report_period_month_radiologist_detail.html", context
    )


def board(request):
    post_list = (
        Post.objects.filter(is_public=True)
        .order_by("-created_at")
        .select_related("author")
    )
    paginator = Paginator(post_list, 10)  # Show 10 posts per page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"posts": page_obj, "side_menu": "board"}
    return render(request, "dashboard/board.html", context)


def detail(request, pk):
    post = Post.objects.get(pk=pk)
    post_attachments = PostAttachment.objects.filter(post=post)
    context = {
        "post": post,
        "post_attachments": post_attachments,
        "side_menu": "blog",
    }
    return render(request, "dashboard/detail.html", context)


def daisyui(request):
    return render(request, "dashboard/daisyui.html")
