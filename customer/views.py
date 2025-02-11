from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Func, F, Q
from minibooks.models import ReportMasterStat
from crm.models import Opportunity
from accounts.models import CustomUser, Profile
from .models import Company, ServiceFee, CustomerLog, CustomerContact, CustomerFiles
from .forms import (
    CompanyForm,
    ServiceFeeForm,
    CustomerLogForm,
    CustomerContactForm,
    CustomerFilesForm,
)
import json


# 중요함 협진병원/고객병원 사용자 생성기능
def add_collab_login_user(request, customer_id):
    company = get_object_or_404(Company, pk=customer_id)
    menu_id = 0
    v_collab = False
    if company.is_tele:
        if company.is_collab:
            menu_id = 84
            v_collab = True
        else:
            menu_id = 80
    else:
        if company.is_collab:
            menu_id = 82
            v_collab = True
        else:
            # 외부 서비스 업체 로그인 사용자 메뉴
            menu_id = 86

    # 기존 사용자가 있는지 확인
    is_exist = CustomUser.objects.filter(username=f"user{company.id}").exists()
    if is_exist:
        existing_user = CustomUser.objects.get(username=f"user{company.id}")

        company.is_collab = v_collab
        company.customuser = existing_user
        company.save()

        existing_user.profile.email = existing_user.email
        existing_user.profile.real_name = existing_user.first_name
        existing_user.profile.cellphone = company.office_phone
        existing_user.profile.save()

        existing_user.menu_id = menu_id
        # 이 부분은 사용자가 엑세스를 통제하기 위한 로직
        # existing_user.is_active = True
        existing_user.save()

        return redirect("customer:detail", company.id)
    else:
        new_user = CustomUser.objects.create_user(
            username=f"user{company.id}",
            email=company.office_email,
            password=f"human{company.id}",
            first_name=company.president_name,
            last_name=company.president_name,
            menu_id=menu_id,
            is_privacy=True,
            is_active=True,
        )
        company.is_collab = v_collab
        company.customuser = new_user
        company.save()
        return redirect("customer:detail", company.id)


def tag_delete(request, company_id, tag_id):
    company = get_object_or_404(Company, pk=company_id)
    print(tag_id)
    tag = company.tags.get(id=tag_id)
    company.tags.remove(tag)
    print(company.tags.all())
    return redirect("customer:detail", company_id)


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


def edit_contact(request, company_id, contact_id):
    company = get_object_or_404(Company, pk=company_id)
    contact = get_object_or_404(CustomerContact, pk=contact_id)
    if request.method == "POST":
        form = CustomerContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            # form.save(commit=False)
            # form.company = company
            # form.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "CustomerContactChanged": None,
                            "showMessage": "Contact updated.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
    else:
        form = CustomerContactForm(instance=contact)
        context = {"company": company, "form": form, "contact": contact}
    return render(request, "customer/edit_contact.html", context)


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
        companies = Company.objects.filter(tags__slug=tag_slug).order_by(ko_kr.asc())
    else:
        q = request.GET.get("q")
        if q:
            q = q.strip()
            companies = Company.objects.filter(
                Q(business_name__icontains=q)
                | Q(president_name__icontains=q)
                | Q(contact_person__icontains=q)
                | Q(ein__icontains=q)
            ).order_by(ko_kr.asc())
            if companies.count() == 1:
                return redirect("customer:detail", companies[0].id)
        else:
            companies = Company.objects.all().order_by(ko_kr.asc())
            # companies = Company.objects.all().order_by("-updated_at")

    if tag_slug or q:
        emails = (
            companies.values_list("office_email", flat=True)
            .filter(~Q(office_email=None))
            .distinct()
        )
        email_list = ", ".join(list(emails)).replace("'", "").strip()

    else:
        email_list = []

    if companies.count() == 1:
        return redirect("customer:detail", companies[0].id)
    paginator = Paginator(companies, 15)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # tags = Company.tags.all()
    tags = Company.tags.annotate(num_times=Count("company")).order_by("-num_times")
    context = {
        "page_obj": page_obj,
        "title": "Customer List",
        "tags": tags,
        "emails": email_list,
    }
    return render(request, "customer/index.html", context)


def filter_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    companies = Company.objects.filter(tags__contains=[tag]).order_by("business_name")
    paginator = Paginator(companies, 10)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "title": "Customer List", "tag": tag}
    return render(request, "customer/index.html", context)


def tag_search(request):
    if request.method == "GET":
        q = request.GET["q"].strip()
        print(q)
        tags = Company.tags.filter(name__icontains=q)
        tags = tags.annotate(num_times=Count("company")).order_by("-num_times")
        # if companies.count() == 1:
        #     return redirect("customer:detail", companies[0].id)
        context = {"tags": tags, "q": q}
        return render(request, "customer/partial_search_tag.html", context)
    else:
        return render(request, "customer/partial_search_tag.html")


def search_company(request):
    if request.method == "GET":
        q = request.GET["q"].strip()
        # print(q)
        companies = Company.objects.filter(Q(business_name__icontains=q) | Q(ein=q))
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
        .annotate(total=Sum("total_count"), total_amount=Sum("total_revenue"))
        .order_by("-adate")
    )
    contracts = ServiceFee.objects.filter(company=company).order_by("-created_at")
    clogs = CustomerLog.objects.filter(
        company=company, deleted_at__isnull=True
    ).order_by("-created_at")
    contacts = CustomerContact.objects.filter(company=company).order_by("name")
    cfiles = CustomerFiles.objects.filter(company=company).order_by("id")
    opps = Opportunity.objects.filter(company=company).order_by("-created_at")[:20]
    # sys_users = CustomUser.objects.filter(id=company.customuser).first()
    print(company.customuser)
    context = {
        "company": company,
        "cm_refers": cm_refers,
        "contracts": contracts,
        "clogs": clogs,
        "contacts": contacts,
        "cfiles": cfiles,
        "opps": opps,
    }

    return render(request, "customer/detail.html", context)


def update(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)

        if form.is_valid():
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
