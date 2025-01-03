from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.db.models import (
    Count,
    Sum,
    Q,
    F,
    DurationField,
    ExpressionWrapper,
    DecimalField,
    FloatField,
    IntegerField,
)
from django.db.models.functions import Cast, Ceil, ExtractWeekDay
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.models import Profile, CustomUser
from customer.models import Company
from product.models import Platform
from .models import (
    UploadHistory,
    ReportMaster,
    ReportMasterStat,
    ReportMasterWeekday,
    ReportMasterPerformance,
    UploadHistoryTrack,
    MagamMaster,
    MagamDetail,
    HumanRules,
    MagamAccounting,
)
from .forms import UploadHistoryForm, MagamMasterForm, CollabUserSignupForm
from .utils import log_uploadhistory
from tablib import Dataset
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from calendar import monthrange
from django.http import HttpResponse


def create_collab_user(request):
    if request.method == "POST":
        form = CollabUserSignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect("minibooks:index")
    else:
        form = CollabUserSignupForm()
    return render(request, "minibooks/create_collab_user.html", {"form": form})


@login_required
def index(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("account_login")
    # Check if the user is a staff member
    if user.is_staff:
        if user.menu_id == 90:
            pass
        else:
            return redirect("blog:index")
    else:
        # 판독의의 경우
        if user.is_doctor:
            return redirect("dashboard:index")
        # 병원(고객)의 경우
        else:
            return redirect("collab:index")
    upload_histories = (
        UploadHistory.objects.annotate(ReportMaster_count=Count("reportmaster"))
        .filter(is_deleted=False)
        .order_by("-created_at")
    )

    context = {"upload_histories": upload_histories}

    return render(request, "minibooks/index.html", context)


@login_required
def history_delete(request, id):
    uh = get_object_or_404(UploadHistory, id=id)

    if request.method == "POST":
        uh.is_deleted = True
        uh.save()
        ReportMaster.objects.filter(uploadhistory=id).delete()
        ReportMasterStat.objects.filter(UploadHistory=id).delete()
        messages.success(request, "Report data deleted successfully.")
        # tracking the upload history
        log_uploadhistory(
            request.user,
            "Data Deleted",
            f"UploadHistory#{id} deleted successfully.",
            uh,
        )
        return redirect("minibooks:index")
    else:
        context = {"uh": uh}
        return render(request, "minibooks/history_delete.html", context)


@login_required
def new_upload(request):
    user = request.user
    # logger.info(f"User: {user}")
    form = UploadHistoryForm()

    if request.method == "POST":
        form = UploadHistoryForm(request.POST, request.FILES)

        if form.is_valid():
            upload_history = form.save(commit=False)
            upload_history.user = user
            upload_history.created_at = timezone.now()
            upload_history.save()
            messages.success(request, "File uploaded successfully.")
            # tracking the upload history
            log_uploadhistory(
                request.user,
                "File Uploaded",
                "File uploaded successfully.",
                upload_history,
            )
            return redirect("minibooks:index")
        else:
            messages.error(request, "An error occurred.")
            return redirect("minibooks:new_upload")
    else:
        today_date = date.today().strftime("%Y-%m-%d")
        form = UploadHistoryForm(initial={"import_date": today_date})
        context = {"import_date": today_date, "form": form}

    return render(request, "minibooks/new_upload.html", context)


@login_required
def clean_data(request, id):
    v_uploadhistory = get_object_or_404(UploadHistory, id=id)

    # v_rawdata = ReportMaster.objects.filter(uploadhistory=id).order_by("id")

    # # 1. 병원명 정리
    # temp_list = v_rawdata.values_list("apptitle", flat=True).distinct()
    # for temp in temp_list:
    #     company = Company.objects.filter(business_name=temp).first()
    #     temp_list2 = v_rawdata.filter(apptitle=temp)
    #     temp_list2.update(company=company)

    # # 2. 의사명 정리
    # temp_list = v_rawdata.values_list("radiologist", flat=True).distinct()
    # for temp in temp_list:
    #     profile = Profile.objects.filter(real_name=temp).first()
    #     temp_list2 = v_rawdata.filter(radiologist=temp)
    #     temp_list2.update(provider=profile)

    # # 3. Modality 정리
    # temp_list = v_rawdata.values_list("equipment", flat=True).distinct()
    # for temp in temp_list:
    #     temp_list2 = v_rawdata.filter(equipment=temp)
    #     if temp == "DR":
    #         temp_list2.update(amodality="CR")
    #     elif temp == "DT":
    #         temp_list2.update(amodality="CR")
    #     else:
    #         temp_list2.update(amodality=temp)

    # # 4. 휴먼영상의핛센터 처리
    # temp_list2 = v_rawdata.filter(apptitle="휴먼영상의학센터")
    # temp_list2.update(is_human_outpatient=True, is_take=False)

    # # 5. is_take 처리
    # temp_list2 = v_rawdata.filter(UploadHistory__platform="TAKE")
    # temp_list2.update(is_take=True)

    # # 6. 일응처리
    # temp_list2 = v_rawdata.filter(stat="일응")
    # temp_list2.update(is_emergency=True)

    v_rawdata = (
        ReportMaster.objects.filter(uploadhistory=id, verified=False)
        .filter(Q(company=None) | Q(provider=None))
        .order_by("id")
    )

    v_rawdata_count = v_rawdata.count()
    messages.info(request, f"Data cleaning started for {v_rawdata_count} rows.")

    ayear = v_uploadhistory.ayear
    amonth = v_uploadhistory.amonth
    # adate = v_uploadhistory.adate

    def get_verified_object(model, field, value):
        obj = model.objects.filter(**{field: value}).first()
        return obj, obj is not None

    i = 0
    for data in v_rawdata:
        print(data.id)
        company, company_verified = get_verified_object(
            Company, "business_name", data.apptitle
        )

        ## 동명이인 처리(임시)
        radiologist = data.radiologist
        radiologist = radiologist.replace(" ", "").replace("\n", "").replace("\t", "")
        if radiologist == "김수진(유방)":
            radiologist = "김수진"
        elif radiologist == "김수진(신경두경부)":
            radiologist = "김수진B"

        radiologist_profile, radiologist_verified = get_verified_object(
            Profile, "real_name", radiologist
        )
        radiologist = radiologist_profile.user if radiologist_verified else None

        # Modality 처리
        equipment = data.equipment
        if equipment == "DR":
            amodality = "CR"
        elif equipment == "DT":
            amodality = "CR"
        else:
            amodality = equipment

        if data.apptitle == "휴먼영상의학센터":
            is_human_outpatient = True
            # is_take = False  # 차감대상. False면 차감대상이 아님
        else:
            is_human_outpatient = False
            # is_take = False  # 차감대상. False면 차감대상이 아님

        # Request Date 처리
        if data.requestdttm:
            try:
                requestdt = timezone.make_aware(
                    timezone.datetime.strptime(data.requestdttm, "%Y-%m-%d %H:%M:%S")
                )
                requestdt_verified = True
            except (ValueError, TypeError):
                if data.pacs != "ONSITE":
                    requestdt = None
                    requestdt_verified = False
                else:
                    requestdt = None
                    requestdt_verified = True
        else:
            requestdt = None
            requestdt_verified = True

        # Request Date 처리
        if data.approveddttm:
            try:
                approvedt = timezone.make_aware(
                    timezone.datetime.strptime(data.approveddttm, "%Y-%m-%d %H:%M:%S")
                )
                approvedt_verified = True
            except (ValueError, TypeError):
                if data.pacs != "ONSITE":
                    approvedt = None
                    approvedt_verified = False
                else:
                    approvedt = None
                    approvedt_verified = True
        else:
            approvedt = None
            approvedt_verified = True

        verified = all(
            [
                company_verified,
                radiologist_verified,
                # platform_verified,
                requestdt_verified,
                approvedt_verified,
            ]
        )
        # 디버그용
        if verified:
            # if i < 10:
            #     print(f"valid ID for data: {data.id}")
            # else:
            #     break

            if isinstance(data.id, int):  # Validate that data.id is a numeric value
                v_count = ReportMaster.objects.filter(id=data.id).count()
                ReportMaster.objects.filter(id=data.id).update(
                    company=company,
                    provider=radiologist,
                    amodality=amodality,
                    #
                    is_human_outpatient=is_human_outpatient,
                    # is_take=is_take,
                    requestdt=requestdt,
                    approvedt=approvedt,
                    verified=True,
                )

                print(f"Data for {data.id} / {i} verified.")
                i += 1
            else:
                print(f"Invalid ID for data: {data.id}")

        else:
            unverified_message = ""
            if not company_verified:
                # print(f"Company verification failed for data id: {data.id}")
                unverified_message += (
                    f"Company verification failed for data id: {data.id}\n"
                )
            if not radiologist_verified:
                # print(f"Radiologist verification failed for data id: {data.id}")
                unverified_message += (
                    f"Radiologist verification failed for data id: {data.id}\n"
                )

            if not requestdt_verified:
                print(f"Request date verification failed for data id: {data.id}")
                unverified_message += (
                    f"Request date verification failed for data id: {data.id}\n"
                )
            if not approvedt_verified:
                print(f"Approval date verification failed for data id: {data.id}")
                unverified_message += (
                    f"Approval date verification failed for data id: {data.id}\n"
                )

            ReportMaster.objects.filter(id=data.id).update(
                verified=False,
                unverified_message=unverified_message,
            )
            break

    v_rawdata = ReportMaster.objects.filter(uploadhistory=id, verified=False)
    total_rows = v_rawdata.count()
    if total_rows == 0:
        v_uploadhistory.verified = True
        v_uploadhistory.save(update_fields=["verified"])
        messages.success(request, "Data cleaned successfully.")
        # tracking the upload history
        log_uploadhistory(
            request.user,
            "Data Cleanning",
            "Data cleanned successfully.",
            v_uploadhistory,
        )
    else:
        messages.error(request, "Fail:Please check the log.")
        log_uploadhistory(
            request.user,
            "Data Cleanning",
            f"Failed: Data for {data.id} not verified.",
            v_uploadhistory,
        )

    return redirect("minibooks:index")


def get_progress(request, id):
    v_uploadhistory = get_object_or_404(UploadHistory, id=id)
    return render(request, "minibooks/progress.html", {"uh": v_uploadhistory})


def current_progress(request, id):
    a_raw = UploadHistory.objects.get(id=id)
    current_progress = ReportMaster.objects.filter(
        uploadhistory=id, verified=True
    ).count()
    total_rows = ReportMaster.objects.filter(uploadhistory=id).count()
    data = {
        "current_progress": current_progress,
        "total_rows": total_rows,
        "id": a_raw.id,
        "p_value": round((current_progress / total_rows) * 100, 2),
    }
    # return JsonResponse(data)
    return render(request, "minibooks/current_progress.html", data)


@login_required
def create_reportmaster(request, id):

    a_raw = UploadHistory.objects.get(id=id)
    platform = a_raw.platform
    ayear = int(a_raw.ayear)
    amonth = int(a_raw.amonth)
    # 해달월의 마지막 날짜를 구함
    last_date = date(ayear, amonth, monthrange(ayear, amonth)[1])
    a_file = a_raw.afile
    # 상수들 준비
    humanic = Company.objects.get(id=1)
    # not use on Nov 2024
    # humanic_platform = Platform.objects.filter(name="HPACS").first()

    # rawdata_resource = rawdataResource()
    dataset = Dataset()
    new_rawdata = a_file
    imported_data = dataset.load(new_rawdata.read(), format="xlsx")
    total_rows = len(imported_data)
    print(
        "Total rows: "
        + str(total_rows)
        + "/File: "
        + str(a_file)
        + "/Platform: "
        + str(platform)
    )
    # imported_data = rawdata_resource.import_data(dataset, dry_run=True)

    check_pre_work_count = ReportMaster.objects.filter(uploadhistory=id).count()
    starting_row = check_pre_work_count

    # if not imported_data.has_errors():
    i = starting_row + 1
    for data in imported_data:
        if data[0] == None:
            print("Skip empty rows" + str(i))
            i += 1
        else:
            try:
                print(i)
                if platform == "ONPACS":
                    ReportMaster.objects.create(
                        apptitle=str(data[0]).strip() if data[0] else "",
                        ein=str(data[1]).strip() if data[1] else "",
                        case_id=str(data[2]).strip() if data[2] else "",
                        name=str(data[3]).strip() if data[3] else "",
                        department=str(data[4]).strip() if data[4] else "",
                        bodypart=str(data[5]).strip() if data[5] else "",
                        modality=str(data[6]).strip() if data[6] else "",
                        equipment=str(data[7]).strip() if data[7] else "",
                        studydescription=str(data[8]).strip() if data[8] else "",
                        imagecount=data[9],
                        accessionnumber=str(data[10]).strip() if data[10] else "",
                        readprice=data[11],
                        reader=str(data[12]).strip() if data[12] else "",
                        approver=str(data[13]).strip() if data[13] else "",
                        radiologist=(
                            str(data[14]).strip().replace("\n", "").replace("\t", "")
                            if data[14]
                            else ""
                        ),
                        radiologist_license=str(data[15]).strip() if data[15] else "",
                        studydate=str(data[16]).strip() if data[16] else "",
                        approveddttm=str(data[17]).strip() if data[17] else "",
                        stat=str(data[18]).strip() if data[18] else "",
                        pacs=str(data[19]).strip() if data[19] else "",
                        requestdttm=str(data[20]).strip() if data[20] else "",
                        ecode=str(data[21]).strip() if data[21] else "",
                        sid=str(data[22]).strip() if data[22] else "",
                        # X column
                        patientid=str(data[23]).strip() if data[23] else "",
                        # Y 휴먼결제하기로 함
                        human_paid_all=str(data[24]).strip() if data[24] else "",
                        ayear=str(ayear).strip() if ayear else "",
                        amonth=str(amonth).strip() if amonth else "",
                        adate=last_date,
                        is_take=False,
                        created_at=date.today(),
                        # verified=False,
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )
                elif platform == "TAKE":
                    ReportMaster.objects.create(
                        apptitle=str(data[0]).strip() if data[0] else "",
                        ein=str(data[1]).strip() if data[1] else "",
                        case_id=str(data[2]).strip() if data[2] else "",
                        name=str(data[3]).strip() if data[3] else "",
                        department=str(data[4]).strip() if data[4] else "",
                        bodypart=str(data[5]).strip() if data[5] else "",
                        modality=str(data[6]).strip() if data[6] else "",
                        equipment=str(data[7]).strip() if data[7] else "",
                        studydescription=str(data[8]).strip() if data[8] else "",
                        imagecount=data[9],
                        accessionnumber=str(data[10]).strip() if data[10] else "",
                        readprice=data[11],
                        reader=str(data[12]).strip() if data[12] else "",
                        approver=str(data[13]).strip() if data[13] else "",
                        radiologist=(
                            str(data[14]).strip().replace("\n", "").replace("\t", "")
                            if data[14]
                            else ""
                        ),
                        radiologist_license=str(data[15]).strip() if data[15] else "",
                        studydate=str(data[16]).strip() if data[16] else "",
                        approveddttm=str(data[17]).strip() if data[17] else "",
                        stat=str(data[18]).strip() if data[18] else "",
                        pacs=str(data[19]).strip() if data[19] else "",
                        requestdttm=str(data[20]).strip() if data[20] else "",
                        ecode=str(data[21]).strip() if data[21] else "",
                        sid=str(data[22]).strip() if data[22] else "",
                        # X column
                        patientid=str(data[23]).strip() if data[23] else "",
                        # 24번 칼럼은 보라매, 건보일산 파일에는 존재하지 않음
                        # human_paid_all=str(data[24]).strip() if data[24] else "",
                        ayear=str(ayear).strip() if ayear else "",
                        amonth=str(amonth).strip() if amonth else "",
                        adate=last_date,
                        is_take=True,
                        created_at=date.today(),
                        # verified=False,
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )

                # 아주 예전 엑셀파일 처리를 위해 사용된 것들 12/20/2024
                # elif platform == "ETC":
                # ReportMaster.objects.create(
                #     apptitle=data[0],
                #     case_id=data[1],
                #     equipment=data[2],
                #     studydescription=data[3],
                #     readprice=data[4],
                #     radiologist=data[5],
                #     ayear=str(ayear).strip() if ayear else "",
                #     amonth=str(amonth).strip() if amonth else "",
                #     created_at=date.today(),
                #     verified=False,
                #     uploadhistory=a_raw,
                #     excelrownum=i,
                # )

                else:
                    ReportMaster.objects.create(
                        apptitle="휴먼영상의학센터",
                        company=humanic,
                        case_id=data[8],
                        name=data[14],
                        bodypart=data[11],
                        equipment=data[9],
                        studydescription=data[15],
                        imagecount=data[17],
                        accessionnumber=data[12],
                        readprice=data[16] if data[16] else 0,
                        approver=data[7],
                        radiologist=data[5],
                        radiologist_license=data[6],
                        studydate=data[1],
                        approveddttm=data[2],
                        pacs="HPACS",
                        # platform=humanic_platform,
                        requestdttm=data[4],
                        patientid=data[13],
                        ayear=str(ayear).strip() if ayear else "",
                        amonth=str(amonth).strip() if amonth else "",
                        adate=last_date,
                        is_human_outpatient=True,
                        is_take=False,
                        created_at=date.today(),
                        verified=False,
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )

                # a_raw.save()
                # Call the Celery task
                # test_celery.delay(i)
                i += 1
            except Exception as e:
                print(f"An error occurred during file upload: {e}")
                messages.error(request, f"An error occurred: {e}")
                log_uploadhistory(
                    request.user,
                    "Data Import",
                    f"Failed: An error occurred at row#{i}: {e}",
                    a_raw,
                )
                return redirect("minibooks:index")

    UploadHistory.objects.filter(id=id).update(imported=True)
    messages.success(request, str(i) + " rows imported successfully.")
    log_uploadhistory(
        request.user,
        "Data Import",
        "Data imported successfully.",
        a_raw,
    )
    return redirect("minibooks:index")


def dry_run(request, id):
    a_raw = UploadHistory.objects.get(id=id)
    # company_list_in_report_master = (
    #     ReportMaster.objects.filter(uploadhistory=a_raw)
    #     .values_list("ein", flat=True)
    #     .distinct()
    # )
    company_list_in_report_master = (
        ReportMaster.objects.filter(uploadhistory=a_raw)
        .values_list("apptitle", flat=True)
        .distinct()
    )

    # doctor_list_in_report_master = (
    #     ReportMaster.objects.filter(uploadhistory=a_raw)
    #     .values_list("radiologist_license", flat=True)
    #     .distinct()
    # )
    doctor_list_in_report_master = (
        ReportMaster.objects.filter(uploadhistory=a_raw)
        .values_list("radiologist", flat=True)
        .distinct()
    )
    no_company_list = []
    no_doctor_list = []

    for company in company_list_in_report_master:
        if Company.objects.filter(business_name=company).exists():
            pass
        else:
            no_company_list.append(company)

    for doctor in doctor_list_in_report_master:
        if Profile.objects.filter(real_name=doctor).exists():
            pass
        else:
            no_doctor_list.append(doctor)
    # for company in company_list_in_report_master:
    #     if Company.objects.filter(ein=company).exists():
    #         pass
    #     else:
    #         no_company_list.append(company)

    # for doctor in doctor_list_in_report_master:
    #     if Profile.objects.filter(license_number=doctor).exists():
    #         pass
    #     else:
    #         no_doctor_list.append(doctor)

    context = {
        "no_company_list": no_company_list,
        "no_doctor_list": no_doctor_list,
    }

    return render(request, "minibooks/dry_run_import.html", context)


def snippet_reportmaster(request, id):
    a_raw = UploadHistory.objects.get(id=id)

    reportmasters = ReportMaster.objects.filter(uploadhistory=id).order_by("id")

    total_rows = reportmasters.count()
    paginator = Paginator(reportmasters, 10)
    page = request.GET.get("page")
    try:
        reportmasters = paginator.page(page)
    except PageNotAnInteger:
        reportmasters = paginator.page(1)
    except EmptyPage:
        reportmasters = paginator.page(paginator.num_pages)

    context = {"rs": reportmasters, "total_rows": total_rows}

    return render(request, "minibooks/snippet_reportmaster.html", context)


# 임시로 사용하는 함수(초기 데이터 입력용)
def initial_dr_data(request):

    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("excel_file")
        print(excel_file)

        # doctor_resource = doctorResource()
        # new_doctor = excel_file
        dataset = Dataset()
        imported_data = dataset.load(excel_file.read(), format="xlsx")

        for data in imported_data:
            if data[0] == None:  # Skip empty rows
                continue
            else:
                temp_doctor_table.objects.create(
                    name=data[0],
                    specialty=data[1],
                    doctor_id=data[2],
                    email=data[3],
                    cv3_id=data[4],
                    onpacs_id=data[5],
                    department=data[6],
                    position=data[7],
                    fee_rate=data[8],
                )

        return redirect("minibooks:temp_doctor")
    else:

        return render(request, "importdata/initial_dr_data.html")


def temp_doctor(request):
    temp_doctor = temp_doctor_table.objects.all()

    return render(request, "importdata/temp_doctor.html", {"data": temp_doctor})


def initial_customer_data(request):
    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("excel_file")
        print(excel_file)

        dataset = Dataset()
        imported_data = dataset.load(excel_file.read(), format="xlsx")

        for data in imported_data:
            if data[0] == None:  # Skip empty rows
                continue
            else:
                temp_customer_table.objects.create(
                    name=data[0],
                    customer_id=data[1],
                )

        print("customer imported")

    return render(request, "importdata/initial_customer_data.html")


@login_required
def aggregate_data(request, upload_history_id):
    uh = get_object_or_404(UploadHistory, id=upload_history_id)
    temp_year = int(uh.ayear)
    temp_month = int(uh.amonth)
    # 해달월의 마지막 날짜를 구함
    last_date = date(temp_year, temp_month, monthrange(temp_year, temp_month)[1])

    try:
        # Aggregate data from ReportMaster
        aggregation = (
            ReportMaster.objects.values(
                "provider",
                "company",
                "ayear",
                "amonth",
                "amodality",
                "is_human_outpatient",
                "is_take",
                "is_emergency",
            )
            .filter(uploadhistory=upload_history_id)
            .annotate(
                total_count=Count("id"),
                total_revenue=Sum("readprice"),
                total_expense=Sum("pay_to_provider"),
            )
        )

        # Insert aggregated data into ReportMasterStat
        for entry in aggregation:
            provider = CustomUser.objects.get(id=entry["provider"])
            company = Company.objects.get(id=entry["company"])
            year = entry["ayear"]
            month = entry["amonth"]
            adate = last_date
            # platform = Platform.objects.get(id=entry["platform"])
            amodality = entry["amodality"]
            emergency = entry["is_emergency"]
            human_outpatient = entry["is_human_outpatient"]
            give_or_take = entry["is_take"]
            total_count = entry["total_count"]
            total_revenue = entry["total_revenue"]
            total_expense = entry["total_expense"]

            print(
                f"Provider: {provider}, Company: {company}, Year: {year}, Month: {month}, Modality: {amodality}, Total Count: {total_count}, Revenue: {total_revenue}"
            )

            # Create or update the ReportMasterStat entry
            ReportMasterStat.objects.update_or_create(
                provider=provider,
                company=company,
                ayear=year,
                amonth=month,
                adate=adate,
                amodality=amodality,
                emergency=emergency,
                human_outpatient=human_outpatient,
                give_or_take=give_or_take,
                UploadHistory=UploadHistory.objects.get(id=upload_history_id),
                defaults={
                    "total_count": total_count,
                    "total_revenue": total_revenue,
                    "total_expense": total_expense,
                },
            )
        UploadHistory.objects.filter(id=upload_history_id).update(aggregated=True)
        messages.success(request, "Data aggregated successfully.")
        log_uploadhistory(
            request.user,
            "Data Aggregation",
            "Data aggregated successfully.",
            UploadHistory.objects.get(id=upload_history_id),
        )

        return redirect("minibooks:index")

    except Exception as e:
        # Handle exceptions (e.g., log the error)
        messages.error(request, f"An error occurred: {e}")
        log_uploadhistory(
            request.user,
            "Data Aggregation",
            f"Failed: An error occurred: {e}",
            UploadHistory.objects.get(id=upload_history_id),
        )
        return redirect("minibooks:index")


@login_required
def aggregate_data_weekday(request, upload_history_id):
    uh = get_object_or_404(UploadHistory, id=upload_history_id)
    temp_year = int(uh.ayear)
    temp_month = int(uh.amonth)
    last_date = date(temp_year, temp_month, monthrange(temp_year, temp_month)[1])

    try:
        aggregation = (
            ReportMaster.objects.filter(uploadhistory=upload_history_id)
            .annotate(weekday=ExtractWeekDay("requestdt"))
            .values("company", "ayear", "amonth", "amodality", "weekday")
            .annotate(total_count=Count("id"))
            .order_by("company", "amodality", "weekday")
        )

        for entry in aggregation:
            company = Company.objects.filter(id=entry["company"]).first()
            if not company:
                continue  # 회사가 존재하지 않으면 다음 항목으로 넘어감

            year = entry["ayear"]
            month = entry["amonth"]
            adate = last_date
            amodality = entry["amodality"]
            if amodality is None:
                amodality = "UNKNOWN"
            weekday_number = entry["weekday"]
            if weekday_number is None:
                weekday_number = -1
            total_count = entry["total_count"]
            if total_count is None:
                total_count = 0

            ReportMasterWeekday.objects.update_or_create(
                company=company,
                ayear=year,
                amonth=month,
                adate=adate,
                amodality=amodality,
                UploadHistory=uh,
                weekday_number=weekday_number,
                defaults={
                    "total_count": total_count,
                },
            )

        messages.success(request, "Data aggregated successfully.")
        # log_uploadhistory 함수 정의 필요
        # log_uploadhistory(request.user, "Data Aggregation by weekday", "Weekday Data aggregated successfully.", uh)

        return redirect("minibooks:index")

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        # log_uploadhistory 함수 정의 필요
        # log_uploadhistory(request.user, "Data Aggregation", f"Failed: An error occurred: {e}", uh)
        return redirect("minibooks:index")


@login_required
def aggregate_data_result(request, upload_history_id):
    # Get the aggregated data
    aggregation = ReportMasterStat.objects.filter(
        UploadHistory=upload_history_id
    ).order_by("ayear", "amonth", "provider", "amodality")
    aggregation = aggregation.select_related("company", "provider__profile")

    # Add the real name of the provider's profile and company business name to the context
    for entry in aggregation:
        entry.provider_real_name = entry.provider.profile.real_name
        entry.company_business_name = entry.company.business_name

    total_rows = aggregation.count()
    # Paginate the data
    paginator = Paginator(aggregation, 10)
    page = request.GET.get("page")
    try:
        aggregation = paginator.page(page)
    except PageNotAnInteger:
        aggregation = paginator.page(1)
    except EmptyPage:
        aggregation = paginator.page(paginator.num_pages)

    context = {"rs": aggregation, "total_rows": total_rows}

    return render(request, "minibooks/partial_aggregate_data_result.html", context)


@login_required
def agg_detail(request, id):
    reportmasterstat = ReportMasterStat.objects.get(id=id)
    reportmasters = (
        ReportMaster.objects.filter(
            provider=reportmasterstat.provider,
            company=reportmasterstat.company,
            ayear=reportmasterstat.ayear,
            amonth=reportmasterstat.amonth,
            # platform=reportmasterstat.platform,
            amodality=reportmasterstat.amodality,
        )
        .annotate(
            time_span=ExpressionWrapper(
                F("approvedt") - F("requestdt"), output_field=DurationField()
            )
        )
        .order_by("id")
    )

    total_rows = reportmasters.count()
    paginator = Paginator(reportmasters, 50)
    page = request.GET.get("page")
    try:
        reportmasters = paginator.page(page)
    except PageNotAnInteger:
        reportmasters = paginator.page(1)
    except EmptyPage:
        reportmasters = paginator.page(paginator.num_pages)

    # for report in reportmasters:
    #     print(report.apptitle)

    context = {"rs": reportmasters, "total_rows": total_rows}

    return render(request, "minibooks/partial_agg_detail.html", context)


def partial_tracking(request, id):
    rs_tracking = UploadHistoryTrack.objects.filter(uploadhistory=id).order_by(
        "-created_at"
    )
    context = {"rs_tracking": rs_tracking}

    return render(request, "minibooks/partial_tracking.html", context)


def apply_rule(request, magam_id, rule_id):
    # Extract parameters from GET request

    magam = MagamMaster.objects.get(id=magam_id)
    syear = magam.ayear
    smonth = magam.amonth

    rule = HumanRules.objects.get(id=rule_id)
    selected_rule = rule.def_name

    if selected_rule == "CRLOW":
        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            amodality="CR",
            readprice__lt=1333,
        )
        count_target_rows = target_rows.count()
        target_rows.update(
            pay_to_provider=1000, pay_to_human=F("readprice" - 1000), is_completed=True
        )

    elif selected_rule == "CTCHESTLOW":
        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            amodality="CT",
            bodypart="CHEST",
            readprice__lt=19600,
        )
        count_target_rows = target_rows.count()
        target_rows.update(pay_to_provider=14700, is_completed=True)
        messages.success(
            request,
            f"Total {count_target_rows} cases are applied Rule 4.2 successfully.",
        )
    # 사용하지 않음
    elif selected_rule == "MRLOW":
        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            amodality="MR",
            readprice__lt=40000,
        )
        count_target_rows = target_rows.count()
        for row in target_rows:
            new_readprice = row.readprice * 0.71
            row.applied_rate = 0.71
            row.pay_to_provider = new_readprice
            row.is_completed = True
            row.save()

        messages.success(
            request,
            f"Total {count_target_rows} cases are applied Rule 4.3 successfully.",
        )

    return redirect("minibooks:index")


def apply_rule_progress_check(request, magam_id, rule_id):

    magam = MagamMaster.objects.get(id=magam_id)
    syear = magam.ayear
    smonth = magam.amonth

    rule = HumanRules.objects.get(id=rule_id)
    selected_rule = rule.def_name

    # 휴먼외래: 김성현, 이재희 원장님 모든 케이스에서 계산 제외
    if selected_rule == "HMOFFDRS":
        pass
    elif selected_rule == "HMOFFUSXARF":
        pass
    elif selected_rule == "HMOUT":
        pass
    elif selected_rule == "CRLOW":
        pass
    elif selected_rule == "CTCHESTLOW":
        pass
    elif selected_rule == "GP":
        pass
    elif selected_rule == "GPONSITE":
        pass
    elif selected_rule == "RQTOAPV":
        pass
    elif selected_rule == "NMRISONSITE":
        pass
    elif selected_rule == "CONVERTDT":
        target_rows = ReportMaster.objects.filter(
            # Q(requestdt__isnull=True) | Q(approvedt__isnull=True)
            Q(approvedt__isnull=True)
        )
        count_target_rows = target_rows.count()
        target_i = count_target_rows

    else:
        pass
    context = {
        "i": target_i,
    }

    return render(request, "minibooks/apply_rule_progress_result.html", context)


@login_required
def apply_rule_progress(request, magam_id, rule_id):

    magam = MagamMaster.objects.get(id=magam_id)
    syear = magam.ayear
    smonth = magam.amonth

    rule = HumanRules.objects.get(id=rule_id)
    selected_rule = rule.def_name

    # 휴먼외래: 김성현, 이재희 원장님 모든 케이스에서 계산 제외
    if selected_rule == "HMOFFDRS":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            provider__in=[72, 73],  # 이재희, 김성현 원장님 제외
            # is_human_outpatient=True,
            # is_take=False,
        )
        count_target_rows = target_rows.count()
        amount_readprice = target_rows.aggregate(Sum("readprice"))["readprice__sum"]
        i = count_target_rows
        target_rows.update(
            pay_to_provider=0,
            pay_to_human=0,
            company_paid=F("readprice") * 1,
            applied_rate=0,
            is_completed=True,
        )
        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows}({amount_readprice}) cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )
    # 휴먼외래: 판독료 계산 1번적용
    elif selected_rule == "HMOFFUSXARF":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            is_human_outpatient=True,
            is_take=False,
            amodality__in=["US", "XR", "RF"],
        )
        count_target_rows = target_rows.count()
        amount_readprice = target_rows.aggregate(Sum("readprice"))["readprice__sum"]
        i = count_target_rows
        target_rows.update(
            pay_to_provider=0,
            pay_to_human=0,
            company_paid=F("readprice") * 1,
            applied_rate=0.0,
            is_completed=True,
        )
        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows}({amount_readprice}) cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 휴먼 외래 정산
    elif selected_rule == "HMOUT":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            is_human_outpatient=True,
            is_take=False,
            is_completed=False,
        )
        count_target_rows = target_rows.count()
        amount_readprice = target_rows.aggregate(Sum("readprice"))["readprice__sum"]
        i = count_target_rows
        target_rows.update(
            pay_to_provider=F("readprice") * 1,
            pay_to_human=0,
            company_paid=F("readprice") * 1,
            applied_rate=1.0,
            is_completed=True,
        )
        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases and ({amount_readprice}) are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 통합: CR 할인 계약 적용
    elif selected_rule == "CRLOW":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            amodality="CR",
            readprice__lt=1333,
            is_completed=False,
            is_human_outpatient=False,
            is_take=False,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        target_rows.update(
            pay_to_provider=1000,
            pay_to_human=F("readprice") - 1000,
            company_paid=F("readprice") * 1,
            applied_rate=ExpressionWrapper(
                1000 / Cast(F("readprice"), FloatField()),
                output_field=DecimalField(max_digits=7, decimal_places=2),
            ),
            is_completed=True,
        )

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )
    # 통합: CT 할인 계약 적용
    elif selected_rule == "CTCHESTLOW":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            amodality="CT",
            readprice__lt=19600,
            is_human_outpatient=False,
            is_take=False,
            is_completed=False,
        )

        count_target_rows = target_rows.count()
        i = count_target_rows

        target_rows.update(
            pay_to_provider=14700,
            pay_to_human=F("readprice") - 14700,
            company_paid=F("readprice") * 1,
            applied_rate=ExpressionWrapper(
                14700 / Cast(F("readprice"), FloatField()),
                output_field=DecimalField(max_digits=7, decimal_places=2),
            ),
            is_completed=True,
        )

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 통합: 일반 판독료 계산
    elif selected_rule == "GP":

        providers = Profile.objects.filter(user__is_doctor=True).order_by("real_name")
        i = 0
        for provider in providers:
            target_rows = ReportMaster.objects.filter(
                ayear=syear,
                amonth=smonth,
                provider=provider.user,
                is_completed=False,
                is_human_outpatient=False,
                is_take=False,
            )
            count_target_rows = target_rows.count()
            fee_rate = provider.fee_rate
            i += count_target_rows
            if count_target_rows > 0:
                target_rows.update(
                    applied_rate=fee_rate,
                    pay_to_provider=ExpressionWrapper(
                        F("readprice") * fee_rate,
                        output_field=IntegerField(),
                    ),
                    pay_to_human=F("readprice") * (1 - fee_rate),
                    company_paid=F("readprice") * 1,
                    is_completed=True,
                )

                magam_detail = MagamDetail.objects.create(
                    magammaster=magam,
                    humanrule=rule,
                    affected_rows=count_target_rows,
                    description=f"Total {count_target_rows} cases of {provider.real_name} are applied Rule-{selected_rule} successfully.",
                    created_at=timezone.now(),
                    is_completed=True,
                )

    # 파견: ONSITE 판독료 계산(일산, 보라매병원으로 된 Excel 데이터만 대상임)
    elif selected_rule == "GPONSITE":

        providers = Profile.objects.filter(user__is_doctor=True).order_by("real_name")
        i = 0
        for provider in providers:
            target_rows = ReportMaster.objects.filter(
                ayear=syear,
                amonth=smonth,
                provider=provider.user,
                # is_completed=False,
                is_human_outpatient=False,
                is_take=True,  # 파견 경우(일산, 보라매병원) 368 87
            )

            count_target_rows = target_rows.count()
            i += count_target_rows
            fee_rate = provider.fee_rate
            if count_target_rows > 0:
                target_rows.update(
                    applied_rate=fee_rate,
                    # pay_to_provider=F("readprice") * fee_rate,
                    # pay_to_human=F("readprice") * (1 - fee_rate),
                    # pay_to_provider=F("readprice") * (1 - fee_rate) * -1,
                    pay_to_provider=ExpressionWrapper(
                        F("readprice") * ((1 - fee_rate) * -1),
                        output_field=DecimalField(max_digits=10, decimal_places=0),
                    ),
                    pay_to_human=F("readprice") * (1 - fee_rate),
                    company_paid=F("readprice") * 1,
                    is_completed=True,
                )

                magam_detail = MagamDetail.objects.create(
                    magammaster=magam,
                    humanrule=rule,
                    affected_rows=count_target_rows,
                    description=f"Total {count_target_rows} cases of {provider.real_name} are applied Rule-{selected_rule} successfully.",
                    created_at=timezone.now(),
                    is_completed=True,
                )

    # 일반 판독요청을 응급으로 처리한 경우
    # 이미 판독료 계산이 완료된 경우에만 대상으로 함
    elif selected_rule == "RGTOER":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            stat="일응",
            is_completed=True,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        amount_readprice = target_rows.aggregate(Sum("readprice"))["readprice__sum"]
        for row in target_rows:
            provider = row.provider
            fee_rate = provider.profile.fee_rate

            # Update the row using save() method
            row.human_paid = ExpressionWrapper(
                F("readprice") * 0.5,
                output_field=DecimalField(max_digits=10, decimal_places=0),
            )
            row.pay_to_provider = ExpressionWrapper(
                F("pay_to_provider") + (F("readprice") * 0.5 * fee_rate),
                output_field=DecimalField(max_digits=10, decimal_places=0),
            )
            row.pay_to_human = ExpressionWrapper(
                F("pay_to_provider") + (F("readprice") * 0.5 * (1 - fee_rate)),
                output_field=DecimalField(max_digits=10, decimal_places=0),
            )
            row.save()

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows}({amount_readprice}) cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 휴 적용하는 룰임
    elif selected_rule == "HMPAIDALL":
        # 이전의 모든 룰적용이 완료된 경우를 대상으로 적용함
        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            human_paid_all__icontains="휴",
            # is_human_paid=True,
            is_completed=True,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        amount_readprice = target_rows.aggregate(Sum("readprice"))["readprice__sum"]

        # 고객병원에서는 부담하지 않고 휴먼에서 매출부담을 모두 떠안음.
        target_rows.update(
            company_paid=0,
            human_paid=F("readprice"),
        )
        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows}({amount_readprice}) cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 전체: 판독 시간 계산
    elif selected_rule == "RQTOAPV":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        for row in target_rows:
            if row.requestdt and row.approvedt:
                temp_time_to_complete = row.approvedt - row.requestdt
                temp_time_to_complete = temp_time_to_complete / timedelta(minutes=1)
                row.time_to_complete = temp_time_to_complete
                row.is_completed = True
                row.save()

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 판독시간 계산 후에 통계테이블에 데이터 작성함
    elif selected_rule == "CSTATPURFORMANCE":

        query = """
        SELECT
            company_id,
            provider_id,
            amodality,
            CASE
                WHEN time_to_complete <= 120 THEN '2h'
                WHEN time_to_complete > 120 AND time_to_complete <= 1440 THEN '1d'
                WHEN time_to_complete > 1440 AND time_to_complete <= 2880 THEN '2d'
                WHEN time_to_complete > 2880 AND time_to_complete <= 10080 THEN '7d'
                ELSE '7d+'
            END AS time_range,
            COUNT(*) AS frequency
        FROM ReportMaster
        WHERE ayear = %s AND amonth = %s AND is_onsite=False AND amodality IN ('CR', 'CT', 'MR')
        GROUP BY time_range, amodality, company_id, provider_id
        ORDER BY company_id, provider_id, amodality, time_range;
        """

        with connection.cursor() as cursor:
            # cursor.execute(query)
            cursor.execute(query, [syear, smonth])  # ayear와 amonth를 안전하게 전달
            results = cursor.fetchall()
            count_results = cursor.rowcount

        i = count_results
        for row in results:
            ReportMasterPerformance.objects.update_or_create(
                ayear=syear,
                amonth=smonth,
                company_id=row[0],
                provider_id=row[1],
                amodality=row[2],
                time_range=row[3],
                frequency=row[4],
            )

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_results,
            description=f"Total {count_results} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 전체: ONSITE 로 표시된 모든 경우에 is_onsite=True 적용
    # 계산에 의미는 없음 그냥 어느 PACS를 사용하느냐의 문제임
    elif selected_rule == "NMRISONSITE":

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            pacs="ONSITE",
        )
        count_target_rows = target_rows.count()
        i = count_target_rows

        target_rows.update(is_onsite=True)

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # 전체: 응급 판독료 표시(통계를 위해서만 사용)
    elif selected_rule == "IS_EMERGENCY":

        target_rows = ReportMaster.objects.filter(
            ayear=syear, amonth=smonth, stat="응급"
        )
        count_target_rows = target_rows.count()
        i = count_target_rows

        target_rows.update(
            is_emergency=True,
        )
        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )
    # 전체: 마감 재확인을 함(휴먼, 파견, 일반 각각의 행수를 합하여 전체 목표 행합계가 일치하는지 확인)
    elif selected_rule == "RECHECK":

        # 작업완료된 마스터테이블의 행수를 확인함
        target_rows = ReportMaster.objects.filter(
            ayear=syear, amonth=smonth, is_completed=True
        )
        count_target_rows = target_rows.count()
        i = count_target_rows

        # 마감작업한 통계테이블의 행수를 확인함
        total_magam_rows = MagamMaster.objects.filter(
            ayear=syear, amonth=smonth
        ).aggregate(Sum("target_rows"))

        count_total_magam_rows = total_magam_rows["target_rows__sum"]

        print(f"Target row is {count_target_rows}, 마감 is {count_total_magam_rows}.")
        # 마감작업한 통계테이블의 완료행수 필드를 업데이트함
        rs_magam = MagamMaster.objects.filter(ayear=syear, amonth=smonth)
        rs_magam.update(
            completed_rows=count_total_magam_rows,
        )

        if count_target_rows == count_total_magam_rows:
            rs_magam.update(
                is_completed=True,
            )
            msg = "Successful"
        else:
            rs_magam.update(
                is_completed=False,
            )
            msg = "Failed"

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Target row is {count_target_rows}, 마감 is {count_total_magam_rows}. {rule.name} does {msg}.",
            created_at=timezone.now(),
            is_completed=True,
        )

    # requestdttm, approveddttm 문자필드의 yyyy/mm/dd/ hh:mm:ss 로 되어 있는 데이터를 datatime 데이터로 변경
    elif selected_rule == "CONVERTDT":

        target_rows = ReportMaster.objects.filter(
            # Q(requestdt__isnull=True) | Q(approvedt__isnull=True)
            Q(approvedt__isnull=True)
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        # The string you want to convert
        # date_string = "2024/08/26 10:27:57"

        # Convert the string to a datetime object
        # datetime_object = datetime.strptime(date_string, "%Y/%m/%d %H:%M:%S")

        j = 0  # Initialize counter

        for row in target_rows:
            if row.approveddttm:  # Check if requestdttm exists
                try:
                    # Parse the string to a datetime object
                    parsed_datetime = datetime.strptime(
                        row.approveddttm, "%Y/%m/%d %H:%M:%S"
                    )

                    # Update the requestdt field
                    row.approvedt = parsed_datetime

                    # Save the row
                    row.save()

                    j += 1
                    print(j)

                except ValueError:
                    # Handle any parsing errors (e.g., if the string doesn't match the expected format)
                    print(f"Error{row.id}")

    # 초기화함(모든 마감작업에 적용되었던 Rule들 초기상태로 되돌림)
    elif selected_rule == "INIT":

        # 마감용 통계데이터 작성(손익계산서용)

        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        target_rows.update(
            is_completed=False,
            is_locked=False,
            adjusted_price=0,
            pay_to_provider=0,
            pay_to_human=0,
            pay_to_service=0,
            company_paid=0,
            human_paid=0,
            applied_rate=0,
        )
        magam_detail = MagamDetail.objects.filter(magammaster=magam)
        magam_detail.delete()

    # 간편 손익계산서용 데이터 작성(사용안하는 중 11/22/2024)
    elif selected_rule == "MAGAMSTAT":
        sales = (
            ReportMasterStat.objects.filter(ayear=syear, amonth=smonth)
            .values("company")
            .annotate(
                magam_rows=Sum("total_count"),
                magam_revenue=Sum("total_revenue"),
            )
        )
        count_target_rows = sales.count()
        j = 0
        for row in sales:
            MagamAccounting.objects.update_or_create(
                ayear=syear,
                amonth=smonth,
                client_id=row["company"],  # Access company as a key from the dictionary
                account_code="100",
                defaults={
                    "account_name": "매출",
                    "account_total": row[
                        "magam_revenue"
                    ],  # Access magam_revenue as a key
                    "account_memo": row["magam_rows"],  # Access magam_rows as a key
                },
            )
            j += 1
            print(j)

        cost = (
            ReportMasterStat.objects.filter(ayear=syear, amonth=smonth)
            .values("provider")
            .annotate(
                magam_rows=Sum("total_count"),
                magam_revenue=Sum("total_expense"),
            )
        )

        # Fetch all profiles related to the providers in a single query
        provider_ids = [row["provider"] for row in cost]
        profiles = Profile.objects.filter(user_id__in=provider_ids).values(
            "user_id", "fee_rate"
        )
        profile_dict = {profile["user_id"]: profile["fee_rate"] for profile in profiles}

        j = 0

        # Iterate over the cost data
        for row in cost:
            # Access the fee_rate from the pre-fetched profile data
            fee_rate = profile_dict.get(
                row["provider"], 0
            )  # Default fee_rate to 0 if not found

            # Calculate the result using magam_revenue (ensure it's properly accessed via dictionary)
            # calc_result = row["magam_revenue"] * fee_rate if row["magam_revenue"] else 0
            calc_result = row["magam_revenue"] if row["magam_revenue"] else 0

            # Update or create MagamAccounting records
            MagamAccounting.objects.update_or_create(
                ayear=syear,
                amonth=smonth,
                provider_id=row["provider"],  # Use provider as client_id
                account_code="200",
                defaults={
                    "account_name": "매출원가",
                    "account_total": calc_result,
                    "account_memo": row["magam_rows"],  # Use magam_rows as memo
                },
            )

            j += 1
            print(f"Processed {j} records.")

        magam_detail = MagamDetail.objects.create(
            magammaster=magam,
            humanrule=rule,
            affected_rows=count_target_rows,
            description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
            created_at=timezone.now(),
            is_completed=True,
        )
        i = count_target_rows

    # 함수를 하나 실행할 때 사용
    elif selected_rule == "UTILITY":

        companies = ReportMaster.objects.all().values("company").distinct()
        i = 0
        for com in companies:
            company = Company.objects.get(id=com["company"])

            # is_exist = CustomUser.objects.filter(username=f"user{company.id}").exists()
            # if is_exist:
            #     existing_user = CustomUser.objects.get(username=f"user{company.id}")
            #     company.is_collab = True
            #     company.customuser = existing_user
            #     company.save()

            #     existing_user.profile.email = existing_user.email
            #     existing_user.profile.real_name = existing_user.first_name
            #     existing_user.profile.cellphone = company.office_phone
            #     existing_user.profile.save()

            #     existing_user.menu_id = menu_id
            #     existing_user.save()

            #     return redirect("customer:detail", company.id)
            # else:
            #     new_user = CustomUser.objects.create_user(
            #         username=f"user{company.id}",
            #         email=company.office_email,
            #         password=f"human{company.id}",
            #         first_name=company.president_name,
            #         last_name=company.president_name,
            #         menu_id=menu_id,
            #         is_privacy=True,
            #         is_active=True,
            #     )
            #     company.is_collab = True
            #     company.customuser = new_user
            #     company.save()

            company.is_tele = True
            company.save()
            i += 1
        print(i, "개의 회사에 대해 적용되었습니다.")

        # 사업자 번호 넎기(초기정보입력)
        # data1 = ReportMaster.objects.filter(ayear=syear, amonth=smonth)
        # ein = data1.values("apptitle", "ein").distinct()
        # # print(ein)
        # companies = Company.objects.all()
        # for company in companies:
        #     bn = company.business_name
        #     for row in ein:
        #         if row["apptitle"] == bn:
        #             company.ein = row["ein"]
        #             company.save()
        #             print(bn)

        # 의사면허 번호 넣기(초기정보입력)
        # data1 = ReportMaster.objects.filter(ayear=syear, amonth=smonth)
        # licen_numbers = data1.values("radiologist", "radiologist_license").distinct()

        # profiles = Profile.objects.all()
        # for profile in profiles:
        #     rn = profile.real_name
        #     for row in licen_numbers:
        #         if row["radiologist"] == rn:
        #             profile.license_number = row["radiologist_license"]
        #             profile.save()
        #             print(rn)

        # count_target_rows = licen_numbers.count()

        # ReportMasterStat 테이블의 adate 필드를 마지막날로 업데이트함
        # temp_rss = ReportMasterStat.objects.filter(ayear=syear, amonth=smonth)
        # first_row = temp_rss.first()
        # temp_ayear = first_row.ayear
        # temp_amonth = first_row.amonth
        # last_day = monthrange(int(temp_ayear), int(temp_amonth))[1]
        # count_target_rows = temp_rss.count()
        # new_adate = f"{temp_ayear}-{temp_amonth}-{last_day}"
        # temp_rss.update(adate=new_adate)

        # for row in temp_rs:
        #     temp_ayear = row.ayear
        #     temp_amonth = row.amonth

        #     last_day = monthrange(int(temp_ayear), int(temp_amonth))[1]
        #     magam_date = f"{temp_ayear}-{temp_amonth}-{last_day}"
        #     row.adate = magam_date
        #     row.save()

        # print(temp_ayear, temp_amonth, magam_date)

        # 해당 PACS 를 사용하는 병원들을 가져온다.
        # target_rows = ReportMaster.objects.all().values("company", "pacs").distinct()
        # for row in target_rows:
        #     # print(row["pacs"], row["company"])
        #     pacs = row["pacs"]
        #     if pacs == "ZOLVUE":
        #         Contract.objects.create(
        #             company_id=row["company"], service_fee_id=10, is_active=True
        #         )
        #     elif pacs == "HPACS":
        #         Contract.objects.create(
        #             company_id=row["company"], service_fee_id=10, is_active=True
        #         )
        #     elif pacs == "INFINITT":
        #         Contract.objects.create(
        #             company_id=row["company"], service_fee_id=2, is_active=True
        #         )
        #     else:
        #         pass

        # target_rows = ReportMaster.objects.all()
        # for row in target_rows:
        #     row.company_paid = row.readprice
        #     row.save()
        # i = target_rows.count()
        # return HttpResponse("Utility function is executed.", count_target_rows)
        # i = count_target_rows
        i = 0

    else:
        pass
    context = {
        "i": i,
        "selected_rule": selected_rule,
    }
    return render(request, "minibooks/magam_apply_rule_progress_result.html", context)


@login_required
def magam_list(request):
    magam_list = MagamMaster.objects.all().order_by("-adate")
    context = {"magam_list": magam_list}
    return render(request, "minibooks/magam_list.html", context)


@login_required
def magam_new(request):
    user = request.user
    form = MagamMasterForm()

    if request.method == "POST":
        form = MagamMasterForm(request.POST)
        selected_ayear = form.data.get("ayear")
        selected_amonth = form.data.get("amonth")
        last_day = monthrange(int(selected_ayear), int(selected_amonth))[1]
        adate = f"{selected_ayear}-{selected_amonth}-{last_day}"
        target_rows = ReportMaster.objects.filter(
            ayear=selected_ayear, amonth=selected_amonth
        )

        if form.is_valid():
            magam = form.save(commit=False)
            magam.user = request.user
            magam.target_rows = target_rows.count()
            magam.adate = adate
            magam.created_at = timezone.now()
            magam.save()
            messages.success(request, "New Magam created successfully.")
            return redirect("minibooks:magam_list")
        else:
            messages.error(request, "An error occurred.")
            return redirect("minibooks:magam_new")
    else:
        form = MagamMasterForm()
        context = {"form": form, "user": user}

    return render(request, "minibooks/magam_new.html", context)


def re_cal_magam(request, id):
    magam = MagamMaster.objects.get(id=id)
    target_rows = ReportMaster.objects.filter(ayear=magam.ayear, amonth=magam.amonth)
    count_target_rows = target_rows.count()
    last_day = monthrange(int(magam.ayear), int(magam.amonth))[1]
    adate = f"{magam.ayear}-{magam.amonth}-{last_day}"
    magam.target_rows = count_target_rows
    magam.adate = adate
    magam.save()
    return redirect("minibooks:magam_list")


def get_open(request, id, is_opened):
    magam = MagamMaster.objects.get(id=id)
    print(is_opened)
    if is_opened == "True":
        temp = False
    else:
        temp = True

    print(temp)
    magam.is_opened = temp
    magam.save()

    return redirect("minibooks:magam_list")


@login_required
def magam_view(request, id):
    magam = MagamMaster.objects.get(id=id)
    count_completed_magam = ReportMaster.objects.filter(
        ayear=magam.ayear, amonth=magam.amonth, is_completed=True
    ).count()

    magam_details = MagamDetail.objects.filter(magammaster=magam).order_by("-id")
    humanrules = HumanRules.objects.all().order_by("rules_order")
    result_humanrules = MagamDetail.objects.filter(magammaster=magam).order_by(
        "-created_at"
    )

    context = {
        "magam": magam,
        "magam_details": magam_details,
        "rules": humanrules,
        "result_humanrules": result_humanrules,
        "count_completed_magam": count_completed_magam,
    }

    return render(request, "minibooks/magam_view.html", context)


# 판독의별 해당 년, 월 판독료 재정산 함수
def re_calc_share(request, ayear, amonth, provider_id):

    provider = get_object_or_404(CustomUser, id=provider_id)
    rs = ReportMaster.objects.filter(provider=provider, ayear=ayear, amonth=amonth)
    total_rows = rs.count()

    # 휴먼외래: 판독료 계산 1번적용.  US, XA, RF 제외
    target_rows = rs.filter(is_human_outpatient=True).exclude(
        Q(amodality="US") | Q(amodality="XA") | Q(amodality="RF")
    )
    count_target_rows = target_rows.count()
    i = count_target_rows
    target_rows.update(
        pay_to_provider=F("readprice") * 1,
        pay_to_human=0,
        applied_rate=1.0,
        is_completed=True,
    )
    # 휴먼외래: US, XA, RF는 별도 판독료 처리
    target_rows = rs.filter(is_human_outpatient=True, amodality__in=["US", "XA", "RF"])
    count_target_rows = target_rows.count()
    i = count_target_rows
    target_rows.update(
        pay_to_provider=0,
        pay_to_human=0,
        applied_rate=0.0,
        is_completed=True,
    )

    # 통합: CR 할인 계약 적용
    target_rows = rs.filter(amodality="CR", readprice__lt=1333)
    count_target_rows = target_rows.count()
    i = count_target_rows
    target_rows.update(
        pay_to_provider=1000,
        pay_to_human=F("readprice") - 1000,
        applied_rate=1000 / F("readprice"),
        is_completed=True,
    )

    # 통합: CT 할인 계약 적용
    target_rows = rs.filter(amodality="CT", readprice__lt=19600)
    count_target_rows = target_rows.count()
    i = count_target_rows

    target_rows.update(
        pay_to_provider=14700,
        pay_to_human=F("readprice") - 14700,
        applied_rate=14700 / F("readprice"),
        is_completed=True,
    )

    # 통합: 일반 판독료 계산
    fee_rate = provider.profile.fee_rate
    print(f"Fee rate: {fee_rate}")
    target_rows = rs.filter(is_human_outpatient=False, is_take=False)
    count_target_rows = target_rows.count()
    i = count_target_rows
    target_rows.update(
        applied_rate=fee_rate,
        pay_to_provider=F("readprice") * fee_rate,
        pay_to_human=F("readprice") * (1 - fee_rate),
        is_completed=True,
    )

    # 파견: ONSITE 판독료 계산(일산, 보라매병원으로 된 Excel 데이터만 대상임)
    target_rows = rs.filter(is_human_outpatient=False, is_take=True)
    count_target_rows = target_rows.count()
    i = count_target_rows
    fee_rate = provider.profile.fee_rate
    target_rows.update(
        applied_rate=fee_rate,
        pay_to_provider=F("readprice") * (1 - fee_rate) * -1,
        pay_to_human=F("readprice") * (1 - fee_rate),
        is_completed=True,
    )

    # 전체: 판독 시간 계산
    # for row in rs:
    #     if row.requestdt and row.approvedt:
    #         temp_time_to_complete = row.approvedt - row.requestdt
    #         temp_time_to_complete = temp_time_to_complete / timedelta(minutes=1)
    #         row.time_to_complete = temp_time_to_complete
    #         row.is_completed = True
    #         row.save()

    return redirect("provider:view_provider", id=provider.id)
