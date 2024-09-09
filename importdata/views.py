from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from accounts.models import Profile
from .models import (
    rawdata,
    temp_doctor_table,
    temp_customer_table,
    importhistory,
    cleanData,
)
from customer.models import Company, Contract, ContractItem, Product, Platform
from .forms import importhistoryForm
from import_export import resources
from tablib import Dataset
from importdata.resources import rawdataResource, doctorResource, customerResource
from datetime import date
import tablib
import logging
from django.core.exceptions import MultipleObjectsReturned


def clean_data(request, id):
    v_importhistory = get_object_or_404(importhistory, id=id)
    v_rawdata = rawdata.objects.filter(importhistory=id)
    verified = False

    for data in v_rawdata:
        try:
            company = Company.objects.filter(business_name=data.apptitle).first()
            if company is None:
                company = None
        except MultipleObjectsReturned:
            logging.error(
                f"Multiple companies found with business_name={data.apptitle}"
            )
            company = Company.objects.filter(business_name=data.apptitle).first()

        try:
            radiologist = Profile.objects.filter(real_name=data.radiologist).first()
            if radiologist is None:
                radiologist = None
                verified = False
            else:
                radiologist = radiologist.user
                verified = True
        except MultipleObjectsReturned:
            logging.error(f"Multiple profiles found with real_name={data.radiologist}")
            radiologist = Profile.objects.filter(real_name=data.radiologist).first()
            verified = False

        # try:
        #     platform = Platform.objects.filter(name=data.pacs).first()
        #     if platform is None:
        #         platform = None
        # except MultipleObjectsReturned:
        #     logging.error(f"Multiple platforms found with name={data.pacs}")
        #     platform = Platform.objects.filter(name=data.pacs).first()

        cleanData.objects.create(
            rawdata=data,
            apptitle=data.apptitle,
            company=company,
            case_id=data.case_id,
            name=data.name,
            department=data.department,
            bodypart=data.bodypart,
            modality=data.modality,
            equipment=data.equipment,
            studydescription=data.studydescription,
            imagecount=data.imagecount,
            accessionnumber=data.accessionnumber,
            readprice=data.readprice,
            reader=data.reader,
            approver=data.approver,
            radiologist=data.radiologist,
            provider=radiologist,
            studydate=data.studydate,
            approveddttm=data.approveddttm,
            stat=data.stat,
            pacs=data.pacs,
            # platform=platform,
            requestdttm=data.requestdttm,
            ecode=data.ecode,
            sid=data.sid,
            patientid=data.patientid,
            ayear=v_importhistory.ayear,
            amonth=v_importhistory.amonth,
            verified=verified,
            created_at=date.today(),
        )
        print(f"Data cleaned: {data.case_id}")
    return redirect("importdata:unverified_data", id=id)


def unverified_data(request, id):
    importhistory = importhistory.objects.get(id=id)
    unverified_data = cleanData.objects.filter(importhistory=id, verified=False)
    context = {"unverified_data": unverified_data}

    return render(request, "importdata/unverified_data.html", context)


def temp_customer(request):
    temp_customer = temp_customer_table.objects.all()

    return render(request, "importdata/temp_customer.html", {"data": temp_customer})


def temp_customer_import(request):
    temp_customer = temp_customer_table.objects.all()

    for data in temp_customer:
        Company.objects.create(
            business_name=data.name,
            clinic_id=data.customer_id,
        )

    return redirect("customer:index")


@transaction.atomic
def create_rawdata(request, id):

    try:
        a_raw = importhistory.objects.get(id=id)
        source_from = a_raw.source_from
        a_file = a_raw.file

        # rawdata_resource = rawdataResource()
        dataset = Dataset()
        new_rawdata = a_file
        imported_data = dataset.load(new_rawdata.read(), format="xlsx")
        # imported_data = rawdata_resource.import_data(dataset, dry_run=True)

        # if not imported_data.has_errors():
        for data in imported_data:

            if source_from == "ONPACS":
                rawdata.objects.create(
                    apptitle=data[0],
                    case_id=data[1],
                    name=data[2],
                    department=data[3],
                    bodypart=data[4],
                    modality=data[5],
                    equipment=data[6],
                    studydescription=data[7],
                    imagecount=data[8],
                    accessionnumber=data[9],
                    readprice=data[10],
                    reader=data[11],
                    approver=data[12],
                    radiologist=data[13],
                    studydate=data[14],
                    approveddttm=data[15],
                    stat=data[16],
                    pacs=data[17],
                    requestdttm=data[18],
                    ecode=data[19],
                    sid=data[20],
                    patientid=data[21],
                    created_at=date.today(),
                    cleaned=False,
                    verified=False,
                    importhistory=a_raw,
                    updated_at=date.today(),
                )
            elif source_from == "ETC":

                rawdata.objects.create(
                    apptitle=data[0],
                    case_id=data[1],
                    equipment=data[2],
                    studydescription=data[3],
                    readprice=data[4],
                    radiologist=data[5],
                    created_at=date.today(),
                    cleaned=False,
                    verified=False,
                    importhistory=a_raw,
                    updated_at=date.today(),
                )
        a_raw.imported = True
        a_raw.save()
        return redirect("importdata:index")

    except Exception as e:
        # logger.error(f"An error occurred during file upload: {e}")
        messages.error(request, f"An error occurred: {e}")
        return redirect("importdata:new_upload")


def new_upload(request):
    user = request.user
    # logger.info(f"User: {user}")
    form = importhistoryForm()

    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("file")
        print(excel_file)

        try:
            import_history = importhistory.objects.create(
                user=user,
                import_date=data.get("import_date"),
                ayear=data.get("ayear"),
                amonth=data.get("amonth"),
                source_from=data.get("source_from"),
                description=data.get("description"),
                file=excel_file,
                created_at=timezone.now(),  # Use timezone.now() for the current date and time
            )
            messages.success(request, "File uploaded successfully.")
            return redirect("importdata:index")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect("importdata:new_upload")

    else:
        today_date = date.today().strftime("%Y-%m-%d")

        form = importhistoryForm(initial={"import_date": today_date})
        context = {"import_date": today_date, "form": form}

    return render(request, "importdata/new_upload.html", context)


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

        return redirect("importdata:temp_doctor")
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


def index(request):

    import_histories = importhistory.objects.annotate(
        rawdata_count=Count("rawdata")
    ).all()

    context = {"import_histories": import_histories}

    return render(request, "importdata/index.html", context)


def history_delete(request, id):
    importhistory.objects.get(id=id).delete()
    return redirect("importdata:index")
