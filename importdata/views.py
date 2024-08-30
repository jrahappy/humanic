from django.shortcuts import render, redirect
from django.db import transaction
from .models import rawdata, importhistory, temp_doctor_table, temp_customer_table
from customer.models import Company, Contract, ContractItem, Product, Platform
from datetime import date
import tablib
from import_export import resources
from tablib import Dataset
from importdata.resources import rawdataResource, doctorResource, customerResource


def temp_customer_clean(request):
    temp_customer = temp_customer_table.objects.all()
    v_ein = 2002020000
    companies = []

    for data in temp_customer:
        companies.append(
            Company(
                business_name=data.name,
                ein=v_ein,
            )
        )
        v_ein += 1

    try:
        with transaction.atomic():
            Company.objects.bulk_create(companies)
            # temp_customer.delete()
            return redirect("customer:index")

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect("importdata:temp_customer_view")


def temp_customer_view(request):
    temp_customer = temp_customer_table.objects.all()

    return render(
        request, "importdata/temp_customer_view.html", {"data": temp_customer}
    )


def create_rawdata(request, id):

    a_raw = importhistory.objects.get(id=id)
    a_file = a_raw.file
    print(a_raw.id)
    rawdata_resource = rawdataResource()
    dataset = Dataset()
    new_rawdata = a_file
    imported_data = dataset.load(new_rawdata.read(), format="xlsx")
    # imported_data = rawdata_resource.import_data(dataset, dry_run=True)

    # if not imported_data.has_errors():
    for data in imported_data:
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

    return redirect("importdata:index")
    # else:
    #     print(imported_data.errors)


def new_upload(request):
    user = request.user
    print(user)
    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("excel_file")

        import_history = importhistory.objects.create(
            user=user,
            import_date=data.get("import_date"),
            description=data.get("description"),
            file=excel_file,
            created_at=date.today(),
        )

        return redirect("importdata:index")

    else:
        today_date = date.today()
        context = {"import_date": today_date}

    return render(request, "importdata/new_upload.html", context)


# 임시로 사용하는 함수(초기 데이터 입력용)
def doctor_list_import(request):
    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("excel_file")
        print(excel_file)

        doctor_resource = doctorResource()
        dataset = Dataset()
        new_doctor = excel_file
        imported_data = dataset.load(new_doctor.read(), format="xlsx")

        for data in imported_data:
            temp_doctor_table.objects.create(
                name=data[0],
                doctor_id=data[1],
            )

        print("imported")

    return render(request, "importdata/doctor_list_import.html")


def customer_list_import(request):
    if request.method == "POST":
        data = request.POST
        excel_file = request.FILES.get("excel_file")

        customer_resource = customerResource()
        dataset = Dataset()
        new_customer = excel_file
        imported_data = dataset.load(new_customer.read(), format="xlsx")

        for data in imported_data:
            temp_customer_table.objects.create(
                name=data[0],
                customer_id=data[1],
            )

        print("customer imported")

    return render(request, "importdata/customer_list_import.html")


def index(request):
    import_history = importhistory.objects.all()

    return render(request, "importdata/index.html", {"data": import_history})
