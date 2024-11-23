from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Func, F, Q
from .models import Company, ServiceFee, CustomerLog, CustomerContact, CustomerFiles
from minibooks.models import ReportMasterStat
from .forms import (
    CompanyForm,
    ServiceFeeForm,
    CustomerLogForm,
    CustomerContactForm,
    CustomerFilesForm,
)
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import json


def tag_delete(request, company_id, tag_id):
    company = get_object_or_404(Company, pk=company_id)
    print(tag_id)
    tag = company.tags.get(id=tag_id)
    company.tags.remove(tag)
    print(company.tags.all())
    return redirect("customer:detail", company_id)
    # return HttpResponse(
    #     status=204,
    #     headers={"HX-Trigger": json.dumps({"CustomerTagsChanged": None})},
    # )


def cfiles(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    cfiles = CustomerFiles.objects.filter(company=company).order_by("id")
    context = {"cfiles": cfiles, "company": company}
    return render(request, "customer/cfiles.html", context)


def cfile_upload(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == "POST":
        form = CustomerFilesForm(request.POST, request.FILES)
        # print(form)
        if form.is_valid():
            files = request.FILES.getlist("file")
            name = request.POST.get("name")
            for file in files:
                file_name = file.name
                CustomerFiles.objects.create(
                    company=company, name=name, file_name=file_name, file=file
                )
                print(file_name)

            # messages.success(request, "HR File uploaded successfully")
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "CustomerfilesChanged": None,
                            "showMessage": "File(s) Added.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            messages.error(request, "Error uploading HR File")
    else:
        form = CustomerFilesForm()

    return render(
        request, "customer/cfile_upload.html", {"company": company, "form": form}
    )


def cfile_delete(request, company_id, cfile_id):
    company = get_object_or_404(Company, pk=company_id)
    cfile = get_object_or_404(CustomerFiles, pk=cfile_id)
    cfile.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "CustomerfilesChanged": None,
                    "showMessage": "File Deleted.",
                }
            )
        },
    )


def contacts(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    contacts = CustomerContact.objects.filter(company=company).order_by("name")
    context = {"company": company, "contacts": contacts}
    return render(request, "customer/contacts.html", context)


def new_contact(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == "POST":
        form = CustomerContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "CustomerContactChanged": None,
                            "showMessage": "Contact created.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
    else:
        form = CustomerContactForm()
        context = {"company": company, "form": form}
    return render(request, "customer/new_contact.html", context)


def delete_contact(request, company_id, contact_id):
    company = get_object_or_404(Company, pk=company_id)
    contact = get_object_or_404(CustomerContact, pk=contact_id)
    contact.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {"CustomerContactChanged": None, "showMessage": "Contact deleted."}
            )
        },
    )


def clogs(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    # print(company)
    clogs = CustomerLog.objects.filter(
        company=company, deleted_at__isnull=True
    ).order_by("-created_at")
    # print(clogs)
    context = {"company": company, "clogs": clogs}
    return render(request, "customer/clogs.html", context)


def new_clog(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    user = request.user
    real_name = user.profile.real_name
    # print(real_name)
    if request.method == "POST":
        form = CustomerLogForm(request.POST)
        # print(form)
        if form.is_valid():
            clog = form.save(commit=False)
            clog.company = company
            clog.updated_by = request.user
            clog.deleted_at = None
            clog.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "CustomerLogChanged": None,
                            "showMessage": "Log created.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
    else:
        form = CustomerLogForm()
        context = {"company": company, "real_name": real_name, "form": form}

    return render(request, "customer/new_clog.html", context)


def delete_clog(request, company_id, clog_id):
    company = get_object_or_404(Company, pk=company_id)
    clog = get_object_or_404(CustomerLog, pk=clog_id)
    clog.deleted_at = timezone.now()
    clog.updated_by = request.user
    clog.save()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "CustomerLogChanged": None,
                    "showMessage": "Log deleted.",
                }
            )
        },
    )


def index(request):
    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    tag_slug = request.GET.get("tag_slug")
    if tag_slug:
        companies = Company.objects.filter(tags__slug=tag_slug).order_by(
            "business_name"
        )
    else:
        q = request.GET.get("q")
        if q:
            companies = Company.objects.filter(
                Q(business_name__icontains=q) | Q(contact_person__icontains=q)
            ).order_by(ko_kr.asc())
            if companies.count() == 1:
                return redirect("customer:detail", companies[0].id)
        else:
            companies = Company.objects.all().order_by(ko_kr.asc())

    paginator = Paginator(companies, 10)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    tags = Company.tags.all()
    tags = Company.tags.annotate(num_times=Count("company")).order_by("-num_times")
    context = {"page_obj": page_obj, "title": "Customer List", "tags": tags}
    return render(request, "customer/index.html", context)


def filter_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    companies = Company.objects.filter(tags__contains=[tag]).order_by("business_name")
    paginator = Paginator(companies, 10)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "title": "Customer List", "tag": tag}
    return render(request, "customer/index.html", context)


def search_company(request):
    if request.method == "GET":
        q = request.GET["q"].strip()
        # print(q)
        companies = Company.objects.filter(business_name__icontains=q)
        # if companies.count() == 1:
        #     return redirect("customer:detail", companies[0].id)
        context = {"companies": companies, "q": q}
        return render(request, "customer/partial_search_company.html", context)
    else:
        return render(request, "customer/partial_search_company.html")


def new(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            bn = request.POST.get("business_name")
            bn = bn.strip()
            is_exist = Company.objects.filter(business_name=bn).exists()
            if is_exist:
                form.add_error("business_name", "이미 존재하는 병원명입니다.")
                return render(request, "customer/new.html", {"form": form})
            else:
                form.save()
                return redirect("customer:index")
        else:
            print(form.errors)
    else:
        form = CompanyForm()
    return render(request, "customer/new.html", {"form": form})


# def validate_business_name(request):
#     bn = request.GET.get("business_name", None)
#     is_taken = Company.objects.filter(business_name=bn).exists()
#     if is_taken:
#         # data["error_message"] = "이미 존재하는 병원명입니다."
#         error_message = "이미 존재하는 병원명입니다."
#     else:
#         error_message = ""
#     # return JsonResponse(data)
#     return error_message


def new_customer(request):
    if request.method == "POST":
        # Process the form data
        # Retrieve the data from the request.POST dictionary
        # Create a new customer object with the retrieved data
        # Save the customer object to the database
        # Redirect to a success page or render a success message
        pass
    else:
        # Render the form for creating a new customer
        return render(request, "customer/new_customer.html")


def detail(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    cm_refers = (
        ReportMasterStat.objects.filter(company=company)
        # .values("ayear", "amonth", "amodality")
        .values("ayear", "amonth", "adate")
        .annotate(total=Count("total_count"), total_amount=Sum("total_revenue"))
        .order_by("-adate")
    )
    contracts = ServiceFee.objects.filter(company=company).order_by("-created_at")
    clogs = CustomerLog.objects.filter(
        company=company, deleted_at__isnull=True
    ).order_by("-created_at")
    contacts = CustomerContact.objects.filter(company=company).order_by("name")
    cfiles = CustomerFiles.objects.filter(company=company).order_by("id")
    context = {
        "company": company,
        "cm_refers": cm_refers,
        "contracts": contracts,
        "clogs": clogs,
        "contacts": contacts,
        "cfiles": cfiles,
    }

    return render(request, "customer/detail.html", context)


def update(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        # print(form)
        # tag validation

        # tag = request.POST.get("tag")
        # if tag == None:
        #     form.tag = ""
        # if tag:
        #     print("there is a tag")
        # else:
        #     form.add_error(
        #         "tag", "태그를 입력하세요. 삭제하려면 보기메뉴에서 x를 입력하세요."
        #     )

        if form.is_valid():
            # form.id = customer_id
            form.save()
            # print("form saved")
            return render(request, "customer/detail.html", {"company": company})
        else:
            print(form.errors)
            context = {"form": form, "company": company}
            return render(request, "customer/update.html", context)

    else:
        form = CompanyForm(instance=company)
        context = {"form": form, "company": company}
    return render(request, "customer/update.html", context)


def edit_customer(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return render(request, "customer/detail.html", {"company": company})
    else:
        form = CompanyForm(instance=company)
    return render(request, "customer/edit_customer.html", {"form": form})


def contracts(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    contracts = ServiceFee.objects.filter(company=company).order_by("-created_at")
    context = {"company": company, "contracts": contracts}
    return render(request, "customer/contracts.html", context)


def delete_contract(request, company_id, contract_id):
    company = get_object_or_404(Company, pk=company_id)
    contract = get_object_or_404(ServiceFee, pk=contract_id)
    contract.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "ContractChanged": None,
                    "showMessage": "Contract deleted.",
                }
            )
        },
    )


# 인피니트 정액 정보 ["CR":160, "MG, RF":600, "CT":1600, "MR":2700]
#
def new_contract(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    business_name = company.business_name

    if request.method == "POST":
        form = ServiceFeeForm(request.POST)

        if form.is_valid():
            service_fee = form.save(commit=False)
            service_fee.company = company  # Set the company field

            if service_fee.service_company.id == 384:
                service_fee.rule = (
                    '["cr":160, "mg":600, "rf":600, "ct":1600, "mr":2700]'
                )
            else:
                service_fee.rule = "[]"
            service_fee.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "ContractChanged": None,
                            "showMessage": "Contract created.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            context = {"form": form, "company": company, "business_name": business_name}
            return render(request, "customer/new_contract.html", context)

    else:
        form = ServiceFeeForm()
        context = {"form": form, "company": company, "business_name": business_name}
        return render(request, "customer/new_contract.html", context)


def new_contract_detail(request, customer_id, contract_id):
    if request.method == "POST":
        # Process the form data
        # Retrieve the data from the request.POST dictionary
        # Create a new contract detail object with the retrieved data
        # Save the contract detail object to the database
        # Redirect to a success page or render a success message
        pass
    else:
        # Render the form for creating a new contract detail
        return render(request, "customer/new_contract_detail.html")
