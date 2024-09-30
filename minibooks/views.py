from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, connection
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, Page, EmptyPage
from accounts.models import Profile, CustomUser
from customer.models import Company, Contract
from product.models import Product, Platform
from .models import (
    UploadHistory,
    ReportMaster,
    ReportMasterStat,
    ReportMasterPerformance,
    UploadHistoryTrack,
    MagamMaster,
    MagamDetail,
    HumanRules,
)
from .forms import UploadHistoryForm, MagamMasterForm
from .utils import log_uploadhistory
from .tasks import upload_file, update_is_onsite
from celery.result import AsyncResult
from import_export import resources
from tablib import Dataset
from datetime import date, timedelta, datetime
import tablib
import logging
from utils.base_func import (
    get_amonth_choices,
    get_ayear_choices,
    get_platform_choices,
    get_amodality_choices,
    get_specialty_choices,
)
from utils.models import ChoiceMaster
from django.db.models import F, DurationField, ExpressionWrapper, fields
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
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
    v_rawdata = ReportMaster.objects.filter(uploadhistory=id, verified=False).order_by(
        "id"
    )
    v_rawdata_count = v_rawdata.count()
    messages.info(request, f"Data cleaning started for {v_rawdata_count} rows.")

    # 휴먼외래, 차감대상, 일반으로 구분하는 정산방법에 대한 구분임 (임시)
    v_platform = v_uploadhistory.platform
    # print(v_platform)
    ayear = v_uploadhistory.ayear
    amonth = v_uploadhistory.amonth

    # if v_platform == "ETC":
    #     studydate = date(int(ayear), int(amonth), 1)
    #     requestdt = studydate
    #     approvedt = studydate
    #     requestdt_verified = True
    #     approvedt_verified = True

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

        # Platform 처리
        if v_platform == "HPACS":
            # Platform 테이블의 ID  값을 넣음
            is_human_outpatient = True
            is_take = False
            platform_verified = True

        elif v_platform == "TAKE":
            is_human_outpatient = False
            is_take = True
            platform_verified = True

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
                    approvedt_verified = True
        else:
            approvedt = None
            approvedt_verified = True

        verified = all(
            [
                company_verified,
                radiologist_verified,
                platform_verified,
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
                # print(f"Count: {v_count}")
                # print(
                #     f"Company: {company} / Radiologist: {radiologist} / Platform: {platform} / Request Date: {requestdt} / Approval Date: {approvedt}"
                # )
                ReportMaster.objects.filter(id=data.id).update(
                    company=company,
                    provider=radiologist,
                    amodality=amodality,
                    # 9/26 추가
                    is_human_outpatient=is_human_outpatient,
                    is_take=is_take,
                    requestdt=requestdt,
                    approvedt=approvedt,
                    verified=True,
                )
                # ReportMaster.objects.filter(id=data.id).update(
                #     company=company,
                #     provider=radiologist,
                #     amodality=amodality,
                #     platform=platform,
                #     requestdt=requestdt,
                #     approvedt=approvedt,
                #     verified=True,
                # )
                print(f"Data for {data.id} / {i} verified.")
                i += 1
            else:
                print(f"Invalid ID for data: {data.id}")

        else:
            unverified_message = ""
            if not company_verified:
                print(f"Company verification failed for data id: {data.id}")
                unverified_message += (
                    f"Company verification failed for data id: {data.id}\n"
                )
            if not radiologist_verified:
                print(f"Radiologist verification failed for data id: {data.id}")
                unverified_message += (
                    f"Radiologist verification failed for data id: {data.id}\n"
                )
            if not platform_verified:
                print(f"Platform verification failed for data id: {data.id}")
                unverified_message += (
                    f"Platform verification failed for data id: {data.id}\n"
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
            # messages.error(request, f"Data for {data.id} not verified.")

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


@login_required
def create_reportmaster(request, id):

    a_raw = UploadHistory.objects.get(id=id)
    platform = a_raw.platform
    ayear = a_raw.ayear
    amonth = a_raw.amonth
    a_file = a_raw.afile
    # 상수들 준비
    humanic = Company.objects.get(id=1)
    humanic_platform = Platform.objects.filter(name="HPACS").first()

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
                if platform == "ONPACS":
                    ReportMaster.objects.create(
                        apptitle=str(data[0]).strip() if data[0] else "",
                        case_id=str(data[1]).strip() if data[1] else "",
                        name=str(data[2]).strip() if data[2] else "",
                        department=str(data[3]).strip() if data[3] else "",
                        bodypart=str(data[4]).strip() if data[4] else "",
                        modality=str(data[5]).strip() if data[5] else "",
                        equipment=str(data[6]).strip() if data[6] else "",
                        studydescription=str(data[7]).strip() if data[7] else "",
                        imagecount=data[8],
                        accessionnumber=str(data[9]).strip() if data[9] else "",
                        readprice=data[10],
                        reader=str(data[11]).strip() if data[11] else "",
                        approver=str(data[12]).strip() if data[12] else "",
                        radiologist=(
                            str(data[13]).strip().replace("\n", "").replace("\t", "")
                            if data[13]
                            else ""
                        ),
                        studydate=str(data[14]).strip() if data[14] else "",
                        approveddttm=str(data[15]).strip() if data[15] else "",
                        stat=str(data[16]).strip() if data[16] else "",
                        pacs=str(data[17]).strip() if data[17] else "",
                        requestdttm=str(data[18]).strip() if data[18] else "",
                        ecode=str(data[19]).strip() if data[19] else "",
                        sid=str(data[20]).strip() if data[20] else "",
                        patientid=str(data[21]).strip() if data[21] else "",
                        ayear=str(ayear).strip() if ayear else "",
                        amonth=str(amonth).strip() if amonth else "",
                        created_at=date.today(),
                        # verified=False,
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )
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
                        case_id=data[7],
                        name=data[13],
                        bodypart=data[14],
                        equipment=data[8],
                        studydescription=data[10],
                        imagecount=data[16],
                        accessionnumber=data[11],
                        readprice=data[15] if data[15] else 0,
                        approver=data[6],
                        radiologist=data[5],
                        studydate=data[1],
                        approveddttm=data[2],
                        pacs="HPACS",
                        platform=humanic_platform,
                        requestdttm=data[4],
                        patientid=data[12],
                        ayear=str(ayear).strip() if ayear else "",
                        amonth=str(amonth).strip() if amonth else "",
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
            .annotate(total_count=Count("id"), total_revenue=Sum("readprice"))
        )

        # Insert aggregated data into ReportMasterStat
        for entry in aggregation:
            provider = CustomUser.objects.get(id=entry["provider"])
            company = Company.objects.get(id=entry["company"])
            year = entry["ayear"]
            month = entry["amonth"]
            # platform = Platform.objects.get(id=entry["platform"])
            amodality = entry["amodality"]
            emergency = entry["is_emergency"]
            human_outpatient = entry["is_human_outpatient"]
            give_or_take = entry["is_take"]
            total_count = entry["total_count"]
            total_revenue = entry["total_revenue"]

            print(
                f"Provider: {provider}, Company: {company}, Year: {year}, Month: {month}, Modality: {amodality}, Total Count: {total_count}, Revenue: {total_revenue}"
            )

            # Create or update the ReportMasterStat entry
            ReportMasterStat.objects.update_or_create(
                provider=provider,
                company=company,
                ayear=year,
                amonth=month,
                amodality=amodality,
                emergency=emergency,
                human_outpatient=human_outpatient,
                give_or_take=give_or_take,
                UploadHistory=UploadHistory.objects.get(id=upload_history_id),
                defaults={"total_count": total_count, "total_revenue": total_revenue},
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
        i = count_target_rows
        target_rows.update(
            pay_to_provider=0,
            pay_to_human=0,
            applied_rate=0,
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
        i = count_target_rows
        target_rows.update(
            pay_to_provider=0,
            pay_to_human=0,
            applied_rate=0.0,
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

    elif selected_rule == "HMOUT":
        target_rows = ReportMaster.objects.filter(
            ayear=syear,
            amonth=smonth,
            is_human_outpatient=True,
            is_take=False,
            is_completed=False,
        )
        count_target_rows = target_rows.count()
        i = count_target_rows
        target_rows.update(
            pay_to_provider=F("readprice") * 1,
            pay_to_human=0,
            applied_rate=1.0,
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
            applied_rate=1000 / F("readprice"),
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

        # target_rows = ReportMaster.objects.filter(
        #     ayear=syear,
        #     amonth=smonth,
        #     amodality="CT",
        #     readprice__lt=19600,
        #     is_completed=False,
        # ).filter(Q(bodypart__icontains="chest") | Q(bodypart__icontains="abdomen"))

        count_target_rows = target_rows.count()
        i = count_target_rows

        target_rows.update(
            pay_to_provider=14700,
            pay_to_human=F("readprice") - 14700,
            applied_rate=14700 / F("readprice"),
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
                    pay_to_provider=F("readprice") * fee_rate,
                    pay_to_human=F("readprice") * (1 - fee_rate),
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
                is_completed=False,
                is_human_outpatient=False,
                is_take=True,  # 파견 경우(일산, 보라매병원)
            )

            count_target_rows = target_rows.count()
            i += count_target_rows
            fee_rate = provider.fee_rate
            if count_target_rows > 0:
                target_rows.update(
                    applied_rate=fee_rate,
                    # pay_to_provider=F("readprice") * fee_rate,
                    # pay_to_human=F("readprice") * (1 - fee_rate),
                    pay_to_provider=F("readprice") * (1 - fee_rate) * -1,
                    pay_to_human=F("readprice") * (1 - fee_rate),
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
                WHEN time_to_complete <= 1 THEN '1hr'
                WHEN time_to_complete > 1 AND time_to_complete <= 3 THEN '3hrs'
                WHEN time_to_complete > 3 AND time_to_complete <= 24 THEN '24hrs'
                WHEN time_to_complete > 24 AND time_to_complete <= 72 THEN '72hrs'
                WHEN time_to_complete > 72 AND time_to_complete <= 168 THEN '7days'
                ELSE 'above '
            END AS time_range,
            COUNT(*) AS frequency
        FROM ReportMaster
        WHERE ayear = %s AND amonth = %s AND amodality IN ('CR', 'CT', 'MR')
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
        from datetime import datetime

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

                except ValueError as e:
                    # Handle any parsing errors (e.g., if the string doesn't match the expected format)
                    print(f"Error{row.id}")

    # 초기화함(모든 마감작업에 적용되었던 Rule들 초기상태로 되돌림)
    elif selected_rule == "INIT":
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
            applied_rate=0,
        )
        magam_detail = MagamDetail.objects.filter(magammaster=magam)
        magam_detail.delete()

        # magam_detail = MagamDetail.objects.create(
        #     magammaster=magam,
        #     humanrule=rule,
        #     affected_rows=count_target_rows,
        #     description=f"Total {count_target_rows} cases are applied {rule.name} successfully.",
        #     created_at=timezone.now(),
        #     is_completed=True,
        # )

    context = {
        "i": i,
    }
    return render(request, "minibooks/magam_apply_rule_progress_result.html", context)


@login_required
def magam_list(request):
    magam_list = MagamMaster.objects.all()
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
        target_rows = ReportMaster.objects.filter(
            ayear=selected_ayear, amonth=selected_amonth
        )

        if form.is_valid():
            magam = form.save(commit=False)
            magam.user = request.user
            magam.target_rows = target_rows.count()
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
