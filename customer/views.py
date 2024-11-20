from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Func, F, Q
from .models import Company, ServiceFee, CustomerLog
from minibooks.models import ReportMasterStat
from .forms import CompanyForm, ServiceFeeForm, CustomerLogForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
import json


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


# Create your views here.
def index(request):
    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )
    q = request.GET.get("q")
    if q:
        companies = (
            Company.objects.filter(
                Q(business_name__icontains=q)
                | Q(contact_person__icontains=q)
                # | Q(office_phone__icontains=q)
                # | Q(office_email__icontains=q)
            )
            # .filter(is_staff=False)
            # .select_related("profile")
            # .annotate(hr_files_count=Count("hrfiles__id"))
            .order_by(ko_kr.asc())
        )
        if companies.count() == 1:
            return redirect("customer:detail", companies[0].id)
    else:
        companies = Company.objects.all().order_by(ko_kr.asc())

    paginator = Paginator(companies, 10)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "title": "Customer List"}
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
            form.save()
            return redirect("customer:index")
    else:
        form = CompanyForm()
    return render(request, "customer/new.html", {"form": form})


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
        .values("ayear", "amonth")
        .annotate(total=Count("total_count"), total_amount=Sum("total_revenue"))
        .order_by("-ayear", "-amonth")
    )
    contracts = ServiceFee.objects.filter(company=company).order_by("-created_at")
    clogs = CustomerLog.objects.filter(
        company=company, deleted_at__isnull=True
    ).order_by("-created_at")
    context = {
        "company": company,
        "cm_refers": cm_refers,
        "contracts": contracts,
        "clogs": clogs,
    }

    return render(request, "customer/detail.html", context)


def update(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        # print(form)
        if form.is_valid():
            # form.id = customer_id
            form.save()
            # print("form saved")
            return render(request, "customer/detail.html", {"company": company})

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
