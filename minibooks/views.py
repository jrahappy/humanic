from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, Page, EmptyPage
from accounts.models import Profile, CustomUser
from customer.models import Company, Contract, ContractItem
from product.models import Product, Platform
from .models import UploadHistory, ReportMaster, ReportMasterStat, UploadHistoryTrack
from .forms import UploadHistoryForm
from .utils import log_uploadhistory
from .tasks import upload_file, my_task
from celery.result import AsyncResult
from import_export import resources
from tablib import Dataset
from datetime import date
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
from django.db.models import F, ExpressionWrapper, DurationField


def index(request):
    upload_histories = (
        UploadHistory.objects.annotate(ReportMaster_count=Count("reportmaster"))
        .filter(is_deleted=False)
        .order_by("-created_at")
    )

    context = {"upload_histories": upload_histories}

    return render(request, "minibooks/index.html", context)


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


# def new_upload(request):
#     user = request.user
#     # logger.info(f"User: {user}")
#     form = UploadHistoryForm()

#     if request.method == "POST":
#         form = UploadHistoryForm(request.POST, request.FILES)

#         if form.is_valid():
#             upload_history = form.save(commit=False)
#             upload_history.user = user
#             upload_history.created_at = timezone.now()

#             uploaded_file = request.FILES["afile"]
#             file_name = uploaded_file.name
#             file_content = uploaded_file.read()

#             # Call the Celery task to handle the file upload
#             upload_file.delay(file_name, file_content)

#             upload_history.save()

#             messages.success(request, "File uploaded successfully.")
#             # tracking the upload history
#             log_uploadhistory(
#                 request.user,
#                 "FileUpload",
#                 "File uploaded successfully.",
#                 upload_history,
#             )
#             return redirect("minibooks:index")
#         else:
#             messages.error(request, "An error occurred.")
#             return redirect("minibooks:new_upload")
#     else:
#         today_date = date.today().strftime("%Y-%m-%d")
#         form = UploadHistoryForm(initial={"import_date": today_date})
#         context = {"import_date": today_date, "form": form}

#     return render(request, "minibooks/new_upload.html", context)


def clean_data(request, id):
    v_uploadhistory = get_object_or_404(UploadHistory, id=id)
    v_rawdata = ReportMaster.objects.filter(uploadhistory=id, verified=False).order_by(
        "id"
    )
    v_rawdata_count = v_rawdata.count()
    messages.info(request, f"Data cleaning started for {v_rawdata_count} rows.")

    v_platform = v_uploadhistory.platform
    print(v_platform)
    ayear = v_uploadhistory.ayear
    amonth = v_uploadhistory.amonth

    if v_platform == "ETC":
        studydate = date(int(ayear), int(amonth), 1)
        requestdt = studydate
        approvedt = studydate
        requestdt_verified = True
        approvedt_verified = True

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
        if v_platform == "ETC":
            # Platform 테이블의 ID  값을 넣음
            platform = 5
            platform_verified = True
        else:
            pacs_value = data.pacs if data.pacs else None
            # ZOLVUE -> HPACS 변경(임시)
            if pacs_value == "ZOLVUE":
                pacs_value = "HPACS"
            elif pacs_value == "None":
                pacs_value = "ETC"

            platform = Platform.objects.filter(name=pacs_value).first()
            if platform:
                platform_verified = True
            else:
                platform_verified = False

        # Request Date 처리
        if v_platform == "ETC":
            # requestdt = None
            requestdt_verified = True
            # approvedt = None
            approvedt_verified = True

        else:
            if data.requestdttm:
                try:
                    requestdt = timezone.make_aware(
                        timezone.datetime.strptime(
                            data.requestdttm, "%Y-%m-%d %H:%M:%S"
                        )
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

            if data.approveddttm:
                try:
                    approvedt = timezone.make_aware(
                        timezone.datetime.strptime(
                            data.approveddttm, "%Y-%m-%d %H:%M:%S"
                        )
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
                    platform=platform,
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
                elif platform == "ETC":

                    ReportMaster.objects.create(
                        apptitle=data[0],
                        case_id=data[1],
                        equipment=data[2],
                        studydescription=data[3],
                        readprice=data[4],
                        radiologist=data[5],
                        created_at=date.today(),
                        verified=False,
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )

                else:
                    ReportMaster.objects.create(
                        apptitle="휴먼영상의학센터",
                        company=humanic,
                        case_id=data[7],
                        name=data[13],
                        bodypart=data[9],
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


# except Exception as e:
#     # logger.error(f"An error occurred during file upload: {e}")
#     messages.error(request, f"An error occurred: {e}")
#     log_uploadhistory(
#         request.user,
#         "Data Import",
#         f"Failed: An error occurred: {e}",
#         a_raw,
#     )
#     return redirect("minibooks:index")


# def create_reportmaster(request, id):
#     v_uploadhistory = get_object_or_404(UploadHistory, id=id)

#     # if request.method == "POST":
#     # Call the Celery task
#     create_reportmaster_task.delay(id)
#     messages.success(request, "Data import task has been initiated.")
#     log_uploadhistory(
#         request.user,
#         "Data Import",
#         "Data imported successfully.",
#         v_uploadhistory,
#     )

#     return redirect("minibooks:index")

# context = {"uploadhistory": v_uploadhistory}
# return render(request, "minibooks/create_reportmaster.html", context)


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


def aggregate_data(request, upload_history_id):
    try:
        # Aggregate data from ReportMaster
        aggregation = (
            ReportMaster.objects.values(
                "provider", "company", "ayear", "amonth", "amodality", "platform"
            )
            .filter(uploadhistory=upload_history_id)
            .annotate(total_count=Count("id"))
        )

        # Insert aggregated data into ReportMasterStat
        for entry in aggregation:
            provider = CustomUser.objects.get(id=entry["provider"])
            company = Company.objects.get(id=entry["company"])
            year = entry["ayear"]
            month = entry["amonth"]
            platform = Platform.objects.get(id=entry["platform"])
            amodality = entry["amodality"]
            total_count = entry["total_count"]

            print(
                f"Provider: {provider}, Company: {company}, Year: {year}, Month: {month}, Platform: {platform}, Modality: {amodality}, Total Count: {total_count}"
            )

            # Create or update the ReportMasterStat entry
            ReportMasterStat.objects.update_or_create(
                provider=provider,
                company=company,
                ayear=year,
                amonth=month,
                platform=platform,
                amodality=amodality,
                defaults={"total_count": total_count},
                UploadHistory=UploadHistory.objects.get(id=upload_history_id),
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


def agg_detail(request, id):
    reportmasterstat = ReportMasterStat.objects.get(id=id)
    reportmasters = (
        ReportMaster.objects.filter(
            provider=reportmasterstat.provider,
            company=reportmasterstat.company,
            ayear=reportmasterstat.ayear,
            amonth=reportmasterstat.amonth,
            platform=reportmasterstat.platform,
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


def apply_rule_4_1(request):
    # ## Rule 4-1 : - 일반촬영 CR 판독단가 1,333원 이하 건 → 1,000원 지급
    selected_ayear = 2024
    selected_amonth = 7

    target_rows = ReportMaster.objects.filter(
        ayear=selected_ayear, amonth=selected_amonth, amodality="CR", readprice__lt=1333
    )
    count_target_rows = target_rows.count()
    target_rows.update(pay_to_provider=1000, is_completed=True)
    messages.success(
        request, f"Total {count_target_rows} cases are applied Rule 4.1 successfully."
    )
    return redirect("minibooks:index")


def apply_rule_4_2(request):
    # ## Rule 4-2 : - Chest CT(비조영) 판독단가 19,600원 이하 건 → 14,700원 조정
    selected_ayear = 2024
    selected_amonth = 7

    target_rows = ReportMaster.objects.filter(
        ayear=selected_ayear,
        amonth=selected_amonth,
        amodality="CT",
        bodypart="CHEST",
        readprice__lt=19600,
    )
    count_target_rows = target_rows.count()
    target_rows.update(pay_to_provider=14700, is_completed=True)
    messages.success(
        request, f"Total {count_target_rows} cases are applied Rule 4.2 successfully."
    )
    return redirect("minibooks:index")


def apply_rule_4_3(request):
    ## Rule 4-3 : - MR 판독단가 40,000원 미만 건 → 71% 조정 (수수료율 구분없이 전체)
    selected_ayear = 2024
    selected_amonth = 7

    target_rows = ReportMaster.objects.filter(
        ayear=selected_ayear,
        amonth=selected_amonth,
        amodality="MR",
        readprice__lt=40000,
    )
    count_target_rows = target_rows.count()
    new_readprice = target_rows.readprice * 0.71
    target_rows.update(
        applied_rate=0.71, pay_to_provider=new_readprice, is_completed=True
    )
    messages.success(
        request, f"Total {count_target_rows} cases are applied Rule 4.2 successfully."
    )
    return redirect("minibooks:index")


def apply_rule_5(request):
    ## Rule 5 : 나머지는 판독의 수수료율에 따라 계산함
    selected_ayear = 2024
    selected_amonth = 7
    auser = request.user

    provider = Profile.objects.get(user=auser)
    fee_rate = provider.fee_rate

    target_rows = ReportMaster.objects.filter(
        ayear=selected_ayear,
        amonth=selected_amonth,
        is_complated=False,
    ).exclude(pacs="ONSITE")

    count_target_rows = target_rows.count()

    target_rows.update(
        applied_rate=fee_rate, pay_to_provider=new_readprice, is_completed=True
    )
    messages.success(
        request, f"Total {count_target_rows} cases are applied Rule 4.2 successfully."
    )
    return redirect("minibooks:index")
