from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Value, CharField, Q, Sum, Count
from django.db.models.functions import Concat, ExtractYear, ExtractMonth
from .models import (
    Refers,
    ReferHistory,
    IllnessCode,
    ReferIllness,
    ReferSimpleDiagnosis,
    SimpleDiagnosis,
    MyIllnessCode,
    MySimpleDiagnosis,
    ReferFile,
)
from .forms import ReferForm, CollabCompanyForm
from accounts.models import CustomUser, Profile, Holidays, WorkHours
from customer.models import Company, CustomerContact
from customer.forms import CompanyForm
from minibooks.models import ReportMaster, ReportMasterStat, MagamMaster
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tablib import Dataset
from allauth.account.forms import ChangePasswordForm
from .resources import IllnessCodeResource, SimpleDiagnosisResource
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import logging
import json
import os
import datetime
import re
from django.contrib.auth import logout
from django.utils import timezone
from collections import defaultdict
from django.conf import settings
import calendar
from utils.base_func import (
    get_amodality_choices,
    get_year_calendar,
    get_month_calendar,
    APPT_DAYS,
    HOLIDAY_CATEGORY,
    TERM_CATEGORY,
    WORKHOURS,
)
from celery.exceptions import CeleryError
from .tasks import customer_month_csv, update_refer_status, update_cosigend_refer_status
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


def working_setting(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    # 요일별 근무시간
    selected_workhours = WorkHours.objects.filter(company=company).order_by(
        "work_weekday"
    )
    selected_workhours_dict = {
        item["work_weekday"]: item["work_hour"]
        for item in selected_workhours.values("work_weekday", "work_hour")
    }
    # 휴일 OFF 등록
    selected_holidays = Holidays.objects.filter(company=company)
    selected_holidays_dict = {
        item["holiday_category"]: item["holidays"]
        for item in selected_holidays.values("holiday_category", "holidays")
    }
    # print(selected_holidays_dict)
    week_days = APPT_DAYS
    workhours = WORKHOURS

    year = timezone.now().year
    months = get_year_calendar(year)

    context = {
        "company": company,
        "week_days": week_days,
        "workhours": workhours,
        "selected_workhours_dict": selected_workhours_dict,
        "months": months,
        "today_date": timezone.now().date(),
        "selected_holidays_dict": selected_holidays_dict,
    }

    return render(request, "collab/working_setting.html", context)


def workhour_create(request, id):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    week_day = request.GET.get("day")
    work_hour = request.GET.get("hour")

    is_workhour = WorkHours.objects.filter(
        company=company, work_weekday=week_day
    ).exists()

    if is_workhour:
        workhour = WorkHours.objects.get(company=company, work_weekday=week_day)
        wh_list = workhour.work_hour if isinstance(workhour.work_hour, list) else []
        # All day 처리
        if work_hour == "99":
            wh_list = [work_hour]
        else:
            if "99" in wh_list:
                wh_list.remove("99")
            if work_hour not in wh_list:
                wh_list.append(work_hour)
        workhour.work_hour = wh_list
        workhour.save()
        # print("old")
    else:
        workhour = WorkHours()
        workhour.company = company
        workhour.work_weekday = week_day
        wh_list = [work_hour]
        workhour.work_hour = wh_list
        workhour.save()
    # print(wh_list)
    selected_workhours = wh_list

    context = {
        "company": company,
        "week_day": week_day,
        "week_days": APPT_DAYS,
        "workhours": WORKHOURS,
        "selected_workhours": selected_workhours,
        "today_date": timezone.now().date(),
    }

    return render(request, "collab/partial/week_day_hours.html", context)


def workhour_remove(request, id):
    user = request.user
    company = Company.objects.get(id=id)
    # print(company)
    week_day = request.GET.get("day")
    work_hour = request.GET.get("hour")

    workhour = WorkHours.objects.get(company=company, work_weekday=week_day)
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
        "company": company,
        "week_day": week_day,
        "week_days": APPT_DAYS,
        "workhours": WORKHOURS,
        "selected_workhours": selected_workhours,
        "today_date": timezone.now().date(),
    }

    return render(request, "collab/partial/week_day_hours.html", context)


# 휴무일 추가(사용자별)
def holiday_create(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    holiday_category = request.GET.get("category")
    # 병의원 휴일등록 'o' 는 병의원 휴일, 'p'는 닥터공휴일
    holiday_category = "o"
    holiday_name = request.GET.get("name")
    holiday_name = "Office"
    month_name = request.GET.get("month_name")
    # 선택된 날짜
    hdate = request.GET.get("hdate")
    month_number = hdate.split("-")[1]
    year_number = hdate.split("-")[0]
    week_days = APPT_DAYS

    is_holiday = Holidays.objects.filter(company=company).exists()

    if is_holiday:
        holiday = Holidays.objects.get(company=company)
        holidays = holiday.holidays if isinstance(holiday.holidays, list) else []
        if hdate not in holidays:
            holidays.append(hdate)
        holiday.holidays = holidays
        # print("max", max(holidays))
        holiday.save()
    else:
        holiday = Holidays()
        holiday.company = company
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
        "company": company,
        "amonth": amonth,
        "week_days": week_days,
        "selected_holidays": selected_holidays,
        "today_date": timezone.now().date(),
    }

    return render(request, "collab/partial/month_calendar.html", context)


def holiday_remove(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    month_name = request.GET.get("month_name")
    # 선택된 날짜
    hdate = request.GET.get("hdate")
    month_number = hdate.split("-")[1]
    year_number = hdate.split("-")[0]
    week_days = APPT_DAYS

    holiday = Holidays.objects.get(company=company)
    holidays = holiday.holidays if isinstance(holiday.holidays, list) else []
    if hdate in holidays:
        holidays.remove(hdate)
    holiday.holidays = holidays
    holiday.save()

    selected_holidays = holiday.holidays
    amonth = get_month_calendar(int(year_number), int(month_number))

    context = {
        "company": company,
        "amonth": amonth,
        "week_days": week_days,
        "selected_holidays": selected_holidays,
        "today_date": timezone.now().date(),
    }

    return render(request, "collab/partial/month_calendar.html", context)


@login_required
def password_change(request):
    company = Company.objects.filter(customuser=request.user).first()
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully updated!")
            update_session_auth_hash(request, form.user)
            return HttpResponse(
                '<script>window.location.href="%s";</script>'
                % reverse_lazy("collab:password_change_done")
            )  # Redirect to success URL using JavaScript if the form is valid

        else:
            messages.error(request, "There was an error in your password update.")
            return render(
                request,
                "collab/password_change.html",
                {"form": form, "company": company},
            )
    else:
        form = ChangePasswordForm(user=request.user)

    context = {
        "form": form,
        "company": company,
    }

    return render(request, "collab/password_change.html", context)


@login_required
def password_change_done(request):
    company = Company.objects.filter(customuser=request.user).first()
    context = {"company": company}
    return render(request, "collab/password_change_done.html", context)


def partial_my_simple_diagonosis_list(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    my_simples = MySimpleDiagnosis.objects.filter(company=refer.company)
    context = {"draft_refer": refer, "my_simples": my_simples}
    return render(request, "collab/partial_my_simple_diagonosis_list.html", context)


def add_my_simple_code(request, refer_id, simple_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    simple = SimpleDiagnosis.objects.get(id=simple_id)
    if not MySimpleDiagnosis.objects.filter(
        company=company, simple_diagnosis=simple
    ).exists():
        my_simple = MySimpleDiagnosis.objects.create(
            company=company, simple_diagnosis=simple
        )
        my_simple.save()
    else:
        print("Already exists")
        # add.message = "Already exists"
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {"MySimplesChanged": None, "showMessage": "Simple added"}
            )
        },
    )


def delete_my_simple_code(request, simple_id):
    my_simple = MySimpleDiagnosis.objects.get(id=simple_id)
    my_simple.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {"MySimplesChanged": None, "showMessage": "Simple added"}
            )
        },
    )


def partial_my_illness_code_list(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    # user = request.user
    # company = Company.objects.filter(customuser=user).first()
    my_illnesses = MyIllnessCode.objects.filter(company=refer.company)
    context = {"draft_refer": refer, "my_illnesses": my_illnesses}
    return render(request, "collab/partial_my_illness_code_list.html", context)


def add_my_illness_code(request, refer_id, illness_id):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    illness = IllnessCode.objects.get(id=illness_id)
    if not MyIllnessCode.objects.filter(company=company, illness_code=illness).exists():
        my_illness = MyIllnessCode.objects.create(company=company, illness_code=illness)
        my_illness.save()
    else:
        print("Already exists")
        # add.message = "Already exists"

    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {"MyIllnessesChanged": None, "showMessage": "Illness added"}
            )
        },
    )


def delete_my_illness_code(request, refer_id, illness_id):
    my_illness = MyIllnessCode.objects.get(id=illness_id)
    my_illness.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {"MyIllnessesChanged": None, "showMessage": "Illness added"}
            )
        },
    )


@login_required
def stat(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    refers = Refers.objects.filter(company=company)
    cosigned_refers = refers.filter(Q(status="Cosigned") | Q(status="Archived"))
    year_month_list = (
        cosigned_refers.annotate(
            year=ExtractYear("cosigned_at"), month=ExtractMonth("cosigned_at")
        )
        .annotate(
            year_month=Concat("year", Value("-"), "month", output_field=CharField())
        )
        .values_list("year_month", flat=True)
        .distinct()
        .order_by("year_month")
    )

    context = {
        "refers": "",
        "company": company,
        "year_month_list": year_month_list,
    }
    return render(request, "collab/stat.html", context)


@login_required
def stat_tele(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    rpms = ReportMasterStat.objects.filter(company=company)
    year_month_list = rpms.values_list("adate", flat=True).distinct().order_by("-adate")

    buttons_year_month = (
        MagamMaster.objects.filter(is_opened=True)
        .values("ayear", "amonth")
        .distinct()
        .order_by("-adate")
    )
    buttons_year_month = sorted(
        buttons_year_month,
        key=lambda x: (int(x["ayear"]), int(x["amonth"])),
        reverse=True,
    )

    # Transform to nested structure
    year_month_map = defaultdict(list)
    for item in buttons_year_month:
        year = int(item["ayear"])
        month = int(item["amonth"])
        year_month_map[year].append(month)

    data_array = [
        {"year": year, "months": sorted(months, reverse=True)}
        for year, months in year_month_map.items()
    ]
    data_array = sorted(data_array, key=lambda x: x["year"], reverse=True)

    context = {
        "rpms": "",
        "company": company,
        "year_month_list": year_month_list,
        "btn_y_m": data_array,
    }
    return render(request, "collab/stat_tele.html", context)


def partial_stat_tele(request):
    user = request.user
    syear = request.GET.get("syear")
    smonth = request.GET.get("smonth")

    # Calculate the last date of the given year and month
    last_day = calendar.monthrange(int(syear), int(smonth))[1]
    adate = f"{syear}-{smonth.zfill(2)}-{str(last_day).zfill(2)}"
    company = Company.objects.filter(customuser=user).first()

    file_name = f"{adate}_{company.id}.csv"
    s3_path = f"customer_csv_files/{company.id}/{file_name}"
    # s3_path = s3_path.lstrip("/")  # Ensure no leading slash for default_storage
    file_full_path = default_storage.url(
        s3_path
    )  # This generates the URL, doesn't check existence

    print(f"DEBUG: s3_path being checked: '{s3_path}'")
    print(f"DEBUG: URL: '{file_full_path}'")

    # https://humanicfiles.s3.us-east-2.amazonaws.com/customer_csv_files/1/2025-02-28_1.csv

    if default_storage.exists(s3_path):
        csv_ox = True
    else:
        csv_ox = False

    print(f"DEBUG: CSV file exist: {csv_ox}")

    logger.info(f"Checking existence for s3_path: {s3_path}")
    csv_exists = default_storage.exists(s3_path)
    logger.info(f"Exists result: {csv_exists}")

    rpms = (
        ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)
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

    # Calculate the last date of the given year and month
    last_day = calendar.monthrange(int(syear), int(smonth))[1]
    adate = f"{syear}-{smonth.zfill(2)}-{str(last_day).zfill(2)}"

    count_rpms = rpms.count()

    # 일반 판독금액 합계
    total_by_onsite = (
        rpms.values("is_take")
        .annotate(
            total_price=Sum("readprice"),
            total_cases=Count("case_id"),
        )
        .order_by("is_onsite")
    )

    total_by_amodality = (
        rpms.values("amodality")
        .annotate(
            total_price=Sum("readprice"),
            total_cases=Count("case_id"),
        )
        .order_by("amodality")
    )

    providers = ReportMaster.objects.filter(ayear=syear, amonth=smonth, company=company)
    providers = (
        providers.values("provider__profile__real_name")
        .distinct()
        .order_by("provider__profile__real_name")
    )

    count_providers = providers.count()

    context = {
        "company": company,
        "company_id": company.id,
        "rpms": rpms,
        "count_rpms": count_rpms,
        "count_providers": count_providers,
        "adate": adate,
        "ayear": syear,
        "amonth": smonth,
        "providers": providers,
        "total_by_onsite": total_by_onsite,
        "total_by_amodality": total_by_amodality,
        "csv_ox": csv_ox,
        "file_full_path": file_full_path,
    }

    return render(request, "collab/partial_stat_tele.html", context)


@login_required
def make_csv_tele(request, company_id, date):
    try:
        # Validate inputs
        try:
            company_id = int(company_id)  # Ensure company_id is an integer
            # Validate date format (e.g., 'YYYY-MM-DD')
            if not isinstance(date, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                raise ValueError("Date must be in YYYY-MM-DD format")
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid input: company_id={company_id}, date={date}, error={str(e)}"
            )
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "showMessage": "Invalid company ID or date format (YYYY-MM-DD required)."
                        }
                    )
                },
            )

        # Trigger the Celery task
        task = customer_month_csv.delay(company_id, date)
        logger.info(
            f"CSV generation task started: task_id={task.id}, company_id={company_id}, date={date}"
        )

        return HttpResponse(
            status=202,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "CSVGenerated": None,
                        "showMessage": "CSV 생성이 시작되었습니다.",
                        "CSVTaskId": task.id,
                    }
                )
            },
        )

    except CeleryError as e:
        logger.exception(
            f"Celery error generating CSV: company_id={company_id}, date={date}, error={str(e)}"
        )
        return HttpResponse(
            status=503,
            headers={
                "HX-Trigger": json.dumps(
                    {
                        "showMessage": "Celery 서비스에 연결할 수 없습니다. 나중에 다시 시도하세요."
                    }
                )
            },
        )
    except Exception as e:
        logger.exception(
            f"Error generating CSV: company_id={company_id}, date={date}, error={str(e)}"
        )
        return HttpResponse(
            status=500,
            headers={
                "HX-Trigger": json.dumps(
                    {"showMessage": "CSV 생성 중 오류가 발생했습니다."}
                )
            },
        )


@login_required
def partial_stat_filtered(request, company_id):
    company = Company.objects.get(id=company_id)
    year_month = request.GET.get("year_month")

    if year_month == "-":
        context = {"refers": "", "company": company, "year": "", "month": ""}
        return render(request, "collab/partial_stat_filtered.html", context)
    else:

        refers = (
            Refers.objects.filter(company=company)
            .filter(Q(status="Cosigned") | Q(status="Archived"))
            .order_by("-cosigned_at")
        )
        year = int(year_month.split("-")[0])
        month = int(year_month.split("-")[1])
        refers = refers.filter(
            cosigned_at__year=year,
            cosigned_at__month=month,
        )
        context = {"refers": refers, "company": company, "year": year, "month": month}
        return render(request, "collab/partial_stat_filtered.html", context)


def refer_archive(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    refer.status = "Archived"
    refer.updated_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, "Archived", "Archived")
    return redirect("collab:index")


def go_archive(request, company_id):
    company = Company.objects.get(id=company_id)
    refers = Refers.objects.filter(
        company=company,
        status__in=["Cosigned", "Cancelled"],
        cosigned_at__lte=datetime.date.today() - datetime.timedelta(days=1),
    )
    if refers:
        i = 0
        for refer in refers:
            refer.status = "Archived"
            refer.save()
            create_history(request, refer.id, "Archived", "Archived")
            i += 1
        print(f"{i} refer archived")
    else:
        print("No refer to archive")


def create_history(request, refer_id, new_status, memo=None):
    refer = Refers.objects.get(id=refer_id)
    re_history = ReferHistory.objects.create(
        refer=refer,
        changed_status=new_status,
        memo=memo,
        changed_by=request.user,
        changed_at=datetime.datetime.now(),
    )
    return re_history


def partial_illness_list(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    illnesses = ReferIllness.objects.filter(refer=refer_id)
    context = {"illnesses": illnesses, "draft_refer": refer}
    return render(request, "collab/partial_illness_list.html", context)


def delete_refer_illness(request, refer_illness_id):
    refer_illness = ReferIllness.objects.get(id=refer_illness_id)
    refer_illness.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "IllnessChanged": None,
                    "showMessage": "Illness deleted",
                }
            )
        },
    )


def create_refer_illness(request, refer_id, illness_id):
    refer = Refers.objects.get(id=refer_id)
    illness = IllnessCode.objects.get(id=illness_id)
    if ReferIllness.objects.filter(refer=refer, illness=illness).exists():
        # message = "Already exists"
        print("Already exists")
        # messages.error(request, "Already exists")
    else:
        new_one = ReferIllness.objects.create(refer=refer, illness=illness)
    # print(new_one)
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "IllnessChanged": None,
                    "showMessage": "Illness added",
                }
            )
        },
    )


def partial_illness_code_search(request, refer_id):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    my_illnesses = MyIllnessCode.objects.filter(company=company)
    refer = Refers.objects.get(id=refer_id)
    context = {"draft_refer": refer, "my_illnesses": my_illnesses}
    return render(request, "collab/partial_illness_code_search.html", context)


def partial_illness_code_list(request, refer_id):
    q = request.GET.get("q")
    print(q)
    if q:
        illnesses = IllnessCode.objects.filter(
            name__icontains=q
        ) | IllnessCode.objects.filter(code__icontains=q)
        paginator = Paginator(illnesses, 20)  # Show 10 illnesses per page
        page = request.GET.get("page")
        try:
            illnesses = paginator.page(page)
        except PageNotAnInteger:
            illnesses = paginator.page(1)
        except EmptyPage:
            illnesses = paginator.page(paginator.num_pages)
    else:
        illnesses = IllnessCode.objects.all()[0:10]

    refer = Refers.objects.get(id=refer_id)
    context = {"illnesses": illnesses, "draft_refer": refer}

    return render(request, "collab/partial_illness_code_list.html", context)


def delete_simple_diagnosis(request, simple_id):

    refer_simple = ReferSimpleDiagnosis.objects.get(id=simple_id)
    refer_simple.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "SimpleDiagnosisChanged": None,
                    "showMessage": "Simple Diagnosis deleted",
                }
            )
        },
    )


def create_simple_diagnosis(request, refer_id, simple_id):
    refer_id = int(refer_id)
    simple_id = int(simple_id)
    # print(refer_id, simple_id)
    refer = Refers.objects.get(id=refer_id)
    simple = SimpleDiagnosis.objects.get(id=simple_id)
    if ReferSimpleDiagnosis.objects.filter(refer=refer, diagnosis=simple).exists():
        # message = "Already exists"
        print("Already exists")
        # messages.error(request, "Already exists")
    else:
        new_one = ReferSimpleDiagnosis.objects.create(refer=refer, diagnosis=simple)
    # print(new_one)
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "SimpleDiagnosisChanged": None,
                    "showMessage": "Simple Diagnosis added",
                }
            )
        },
    )


def partial_simple_list(request, refer_id):
    # print(refer_id)
    refer = Refers.objects.get(id=refer_id)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    # print(simples.count())
    context = {"simples": simples, "draft_refer": refer}
    return render(request, "collab/partial_simple_list.html", context)


def partial_simple_diagnosis_list(request, refer_id):
    q = request.GET.get("q")
    if q:
        sims = SimpleDiagnosis.objects.filter(short_name__icontains=q).order_by("order")
    else:
        sims = SimpleDiagnosis.objects.all().order_by("order")

    refer = Refers.objects.get(id=refer_id)
    my_simples = MySimpleDiagnosis.objects.filter(company=refer.company)
    filtered = request.GET.get("filtered")

    v_html = ""
    v_step = -1
    v_code = ""
    header_flag = False
    header2_flag = False
    header3_flag = False

    i = 0
    for sim in sims:
        temp_htmx = "<div class='flex flex-row justify-between items-center w-full mb-2 me-2 border-b border-t border-gray-300 hover:bg-gray-200'>"
        if sim.is_head:
            if sim.step == 0:
                temp_header = temp_htmx + f"<h3>{sim.code1}</h3>"
            elif sim.step == 1:
                temp_header = f"<h3 class='mt-4'>{sim.code1}</h3>"
                temp_header += temp_htmx + f"<p class='text-sm ps-2'>--{sim.code2}</p>"
            elif sim.step == 2:
                temp_header = f"<h3 class='mt-4'>{sim.code1}</h3>"
                temp_header += f"<p class='text-sm ps-2'>--{sim.code2} </p>"
                temp_header += (
                    temp_htmx + f"<p class='text-sm ps-2'>----{sim.code3}</p>"
                )
            else:
                temp_header = f"<h3 class='mt-4 mb-1'>{sim.code1}</h3>"
                temp_header += f"<p class='text-sm ps-2 mb-1'>--{sim.code2}</p>"
                temp_header += f"<p class='text-sm ps-2 mb-1'>----{sim.code3}</p>"
                temp_header += (
                    temp_htmx + f"<p class='text-sm ps-2'>------{sim.code4}</p>"
                )

        else:
            if sim.step == 0:
                temp_header = (
                    temp_htmx + f"<p class='text-sm mb-1 font-semibold'>{sim.code1}</p>"
                )
            elif sim.step == 1:
                temp_header = temp_htmx + f"<p class='text-sm ps-2'>--{sim.code2}</p>"
            elif sim.step == 2:
                temp_header = temp_htmx + f"<p class='text-sm ps-2'>----{sim.code3}</p>"
            else:
                temp_header = (
                    temp_htmx + f"<p class='text-sm ps-2'>------{sim.code4}</p>"
                )
        temp_header += (
            f"<div class='flex flex-row justify-end items-center gap-2'>"
            f"<a href='#' class='btn btn-xs btn-primary' "
            f"hx-target='#simple_diagonosis_list_box' "
            f"hx-get='/collab/create_simple_diagnosis/{refer.id}/{sim.id}'>검사추가</a>"
        )
        temp_header += (
            f"<a href='#' class='btn btn-xs btn-secondary' "
            f"hx-target='#my_simple_list'"
            f"hx-get='/collab/add_my_simple_code/{refer.id}/{sim.id}'>+</a>"
        )

        temp_header += "</div></div>"
        # print(temp_header)
        v_step = sim.step
        v_html += temp_header
        i += 1

    if filtered:
        return render(
            request,
            "collab/partial_simple_diagnosis_list_filtered.html",
            {"html": v_html, "draft_refer": refer, "my_simples": my_simples},
        )
    else:
        return render(
            request,
            "collab/partial_simple_diagnosis_list.html",
            {"html": v_html, "draft_refer": refer, "my_simples": my_simples},
        )


def illness_list(request):
    user = request.user
    user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    illnesses = IllnessCode.objects.all()
    paginator = Paginator(illnesses, 10)  # Show 10 illnesses per page
    page = request.GET.get("page")
    try:
        illnesses = paginator.page(page)
    except PageNotAnInteger:
        illnesses = paginator.page(1)
    except EmptyPage:
        illnesses = paginator.page(paginator.num_pages)

    context = {"illnesses": illnesses, "company": company}
    return render(request, "collab/illness_list.html", context)


def illness_code_import(request):
    user = request.user
    # user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    if request.method == "POST":
        illness_resource = IllnessCodeResource()
        dataset = Dataset()
        new_illness = request.FILES["myfile"]
        print(new_illness)

        dataset.load(new_illness.read(), format="xlsx")
        result = illness_resource.import_data(dataset, dry_run=True)

        for row in result:
            for error in row.errors:
                print(error)

        if not result.has_errors():
            illness_resource.import_data(dataset, dry_run=False)
        else:
            print(result.errors)

        return redirect("collab:illness_list")

    else:
        context = {"company": company}
        return render(request, "collab/illness_code_import.html", context)


def simplecode_list(request):
    user = request.user
    user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    simples = SimpleDiagnosis.objects.all()
    paginator = Paginator(simples, 10)  # Show 10 illnesses per page
    page = request.GET.get("page")
    try:
        illnesses = paginator.page(page)
    except PageNotAnInteger:
        illnesses = paginator.page(1)
    except EmptyPage:
        illnesses = paginator.page(paginator.num_pages)

    context = {"simples": simples, "company": company}
    return render(request, "collab/simplecode_list.html", context)


def simplecode_import(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()

    if request.method == "POST":
        simple_resource = SimpleDiagnosisResource()
        dataset = Dataset()
        new_simple = request.FILES["myfile"]
        dataset.load(new_simple.read(), format="xlsx")
        result = simple_resource.import_data(dataset, dry_run=True)

        for row in result:
            for error in row.errors:
                print(error)
        if not result.has_errors():
            simple_resource.import_data(dataset, dry_run=False)
        else:
            print(result.errors)
        return redirect("collab:simplecode_list")
    else:
        context = {"company": company}
        return render(request, "collab/simplecode_import.html", context)


# def home(request):
#     user = request.user
#     refers = Refers.objects.all().order_by("-created_at")
#     paginator = Paginator(refers, 10)  # Show 10 refers per page
#     page = request.GET.get("page")
#     try:
#         refers = paginator.page(page)
#     except PageNotAnInteger:
#         refers = paginator.page(1)
#     except EmptyPage:
#         refers = paginator.page(paginator.num_pages)
#     context = {"refers": refers}
#     return render(request, "collab/home.html", context)


@login_required
def home(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()

    # Draft refer를 무조건 하나 만들어둔다. 추가함.
    draft_exists = Refers.objects.filter(company=company, status="Draft").exists()
    if not draft_exists:
        # referred_date = datetime.date.today()
        Refers.objects.create(
            company=company,
            status="Draft",
            # referred_date=referred_date,
            # patient_birthdate=patient_birthdate,
        )
        print("Draft refer created")

    q = request.GET.get("q")
    if q:
        refers = (
            Refers.objects.filter(company=company, patient_name__icontains=q)
            .exclude(status="Draft")
            .order_by("-created_at")
        )
    else:
        refers = (
            Refers.objects.filter(company=company)
            .exclude(status="Draft")
            .order_by("-created_at")
        )
    paginator = Paginator(refers, 15)  # Show 10 refers per page
    page = request.GET.get("page")
    try:
        refers = paginator.page(page)
    except PageNotAnInteger:
        refers = paginator.page(1)
    except EmptyPage:
        refers = paginator.page(paginator.num_pages)
    context = {"refers": refers, "company": company}
    return render(request, "collab/home.html", context)


def index(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    if not company:
        logout(request)
        return redirect("web:index")
    # Archive old refers
    # go_archive(request, company.id)

    print(user.menu_id)

    q = request.GET.get("q")
    if q:
        refers = Refers.objects.filter(
            company=company, patient_name__icontains=q
        ).order_by("-created_at")
    else:
        refers = (
            Refers.objects.filter(company=company)
            .exclude(status="Draft")
            .order_by("-created_at")
        )
    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")
    status_cancelled = refers.filter(status="Cancelled")[0:5]

    # Draft refer를 무조건 하나 만들어둔다.
    draft_exists = Refers.objects.filter(company=company, status="Draft").exists()
    if not draft_exists:
        # referred_date = datetime.date.today()
        Refers.objects.create(
            company=company,
            status="Draft",
            # referred_date=referred_date,
            # patient_birthdate=patient_birthdate,
        )
        print("Draft refer created")

    context = {
        "refers": refers,
        "company": company,
        "draft_exist": draft_exists,
        "status_rq": status_rq,
        "status_rq_count": status_rq.count(),
        "status_sch": status_sch,
        "status_sch_count": status_sch.count(),
        "status_in": status_in,
        "status_in_count": status_in.count(),
        "status_cosign": status_cosign,
        "status_cosign_count": status_cosign.count(),
        "status_cancelled": status_cancelled,
        "status_cancelled_count": status_cancelled.count(),
    }
    return render(request, "collab/index.html", context)


@login_required
def refer_list(request, company_id):
    company = Company.objects.get(id=company_id)
    # Archive old refers
    # go_archive(request, company.id)

    q = request.GET.get("q")
    if q:
        refers = Refers.objects.filter(
            company=company, patient_name__icontains=q
        ).order_by("-created_at")
    else:
        refers = Refers.objects.exclude(status="Draft", company=company).order_by(
            "-created_at"
        )
    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")
    status_cancelled = refers.filter(status="Cancelled")

    context = {
        "refers": refers,
        "company": company,
        # "draft_exist": draft_exists,
        "status_rq": status_rq,
        "status_rq_count": status_rq.count(),
        "status_sch": status_sch,
        "status_sch_count": status_sch.count(),
        "status_in": status_in,
        "status_in_count": status_in.count(),
        "status_cosign": status_cosign,
        "status_cosign_count": status_cosign.count(),
        "status_cancelled": status_cancelled,
        "status_cancelled_count": status_cancelled.count(),
    }
    return render(request, "collab/refer_list.html", context)


# def partial_simple_list(request):
#     refer_simples = ReferSimpleDiagnosis.objects.filter(refer=refer_id)
#     context = {"refer_simples": refer_simples}
#     return render(request, "collab/partial_simple_list.html", context)


def clean_refer(request):
    user = request.user
    # update_refer_status.delay()
    HumanIC = CustomUser.objects.get(username="HumanIC")

    refers = Refers.objects.filter(
        status__in=["Cosigned"],
        referred_date__lt=timezone.now() - datetime.timedelta(days=7),
    ).order_by("referred_date")

    updated_count = 0
    for refer in refers:

        next_status = "Archived"
        refer.status = next_status
        refer.updated_at = timezone.now()
        refer.save()
        ReferHistory.objects.create(
            refer=refer,
            changed_status="Cancelled",
            memo="Refer archived.",
            changed_by=HumanIC,
            changed_at=timezone.now(),
        )

        updated_count += 1

    print(
        f"DEBUG: {updated_count} refers updated to 'Cancelled' status due to inactivity."
    )
    messages.success(
        request,
        f"{updated_count} refers updated to 'Cancelled' status due to inactivity.",
    )
    return redirect("crm:collab_kanban")


def refer_create(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    draft_refer = Refers.objects.filter(company=company, status="Draft").first()
    # 오늘 날짜로 업데이트를 해준다.
    # draft_refer.referred_date = datetime.date.today()
    # draft_refer.referred_date = datetime.datetime.now(tz=datetime.UTC).date()
    draft_refer.referred_date = timezone.localtime(timezone.now()).date()
    draft_refer.save()

    # print(draft_refer.id)
    if request.method == "POST":
        form = ReferForm(request.POST, instance=draft_refer)
        simples = ReferSimpleDiagnosis.objects.filter(refer=draft_refer)
        illnesses = ReferIllness.objects.filter(refer=draft_refer)
        # print("valid form?")
        if form.is_valid():
            new_status = "Requested"
            form.save(commit=False)
            form.instance.company = company
            # form.instance.refer_doctor = company.president_name
            form.instance.status = new_status
            form.save()
            create_history(request, draft_refer.id, new_status, "Refer created")
            return redirect("collab:refer_detail", refer_id=draft_refer.id)
        else:
            print(form.errors)
            context = {
                "form": form,
                "company": company,
                "draft_refer": draft_refer,
                "simples": simples,
                "illnesses": illnesses,
            }
            return render(request, "collab/refer_create.html", context)
    else:
        simples = ReferSimpleDiagnosis.objects.filter(refer=draft_refer)
        simples.delete()
        illnesses = ReferIllness.objects.filter(refer=draft_refer)
        illnesses.delete()

        form = ReferForm(instance=draft_refer)
        context = {
            "form": form,
            "company": company,
            "draft_refer": draft_refer,
            "simples": simples,
            "illnesses": illnesses,
        }
        return render(request, "collab/refer_create.html", context)


def refer_detail(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    history = ReferHistory.objects.filter(refer=refer)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    illnesses = ReferIllness.objects.filter(refer=refer)
    files = ReferFile.objects.filter(refer=refer)
    context = {
        "refer": refer,
        "simples": simples,
        "illnesses": illnesses,
        "company": company,
        "history": history,
        "files": files,
    }
    return render(request, "collab/refer_detail.html", context)


def refer_print(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    # history = ReferHistory.objects.filter(refer=refer)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    illnesses = ReferIllness.objects.filter(refer=refer)
    context = {
        "refer": refer,
        "simples": simples,
        "illnesses": illnesses,
        "company": company,
        # "history": history,
    }
    return render(request, "collab/refer_print.html", context)


def return_report_print(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    # history = ReferHistory.objects.filter(refer=refer)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    illnesses = ReferIllness.objects.filter(refer=refer)
    context = {
        "refer": refer,
        "simples": simples,
        "illnesses": illnesses,
        "company": company,
        # "history": history,
    }
    return render(request, "collab/return_report_print.html", context)


def refer_update(request, refer_id):
    draft_refer = Refers.objects.get(id=refer_id)
    company = draft_refer.company
    simples = ReferSimpleDiagnosis.objects.filter(refer=draft_refer)
    illnesses = ReferIllness.objects.filter(refer=draft_refer)

    # print(draft_refer.id)
    if request.method == "POST":
        form = ReferForm(request.POST, instance=draft_refer)
        print("valid form?")
        if form.is_valid():
            new_status = "Requested"
            form.save(commit=False)
            form.instance.company = company
            form.instance.status = new_status
            form.save()
            new_history = create_history(
                request, draft_refer.id, new_status, "Refer updated"
            )
            return redirect("collab:refer_detail", refer_id=draft_refer.id)
        else:
            print(form.errors)
            context = {
                "form": form,
                "company": company,
                "draft_refer": draft_refer,
                "simples": simples,
                "illnesses": illnesses,
            }
            return render(request, "collab/refer_update.html", context)
    else:
        form = ReferForm(instance=draft_refer)
        context = {
            "form": form,
            "company": company,
            "draft_refer": draft_refer,
            "simples": simples,
            "illnesses": illnesses,
        }
        return render(request, "collab/refer_update.html", context)


def refer_delete(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    # refer_simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    # refer_simples.delete()
    # refer_illnesses = ReferIllness.objects.filter(refer=refer)
    # refer_illnesses.delete()
    refer.delete()

    return redirect("collab:index")


def refer_completed(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    new_status = "Cosigned"
    refer.status = new_status
    refer.cosigned_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, new_status, "협진(Co-sign) 완료")
    return redirect("collab:index")


def company_info(request, company_id):
    company = Company.objects.get(id=company_id)
    contacts = CustomerContact.objects.filter(company=company)
    # refers = Refers.objects.filter(company=company)
    context = {"company": company, "contacts": contacts}
    return render(request, "collab/company_info.html", context)


def company_update(request, company_id):
    company = Company.objects.get(id=company_id)
    contacts = CustomerContact.objects.filter(company=company)
    if request.method == "POST":
        form = CollabCompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("collab:company_info", company_id=company.id)

    else:
        form = CollabCompanyForm(instance=company)

    context = {"company": company, "contacts": contacts, "form": form}
    return render(request, "collab/company_update.html", context)


def profile(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    profile = Profile.objects.filter(user=user).first()
    context = {"profile": profile, "company": company}
    return render(request, "collab/profile.html", context)
