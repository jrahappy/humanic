from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from .models import Company, Contract
from minibooks.models import ReportMasterStat, ReportMaster
from .forms import CompanyForm

# from importData.models import cleanData
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    companies = Company.objects.all().order_by("business_name")
    paginator = Paginator(companies, 10)  # Show 10 companies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "title": "Customer List"}
    return render(request, "customer/index.html", context)


def search_company(request):
    if request.method == "GET":
        q = request.GET["q"].strip()
        companies = Company.objects.filter(business_name__icontains=q)
        # if companies.count() == 1:
        #     return redirect("customer:detail", companies[0].id)
        context = {"companies": companies, "q": q}
        return render(request, "customer/partial_search_company.html", context)
    else:
        return render(request, "customer/partial_search_company.html")


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
        .values("ayear", "amonth", "amodality")
        .annotate(total=Count("total_count"), total_amount=Sum("total_revenue"))
        .order_by("-ayear", "-amonth", "amodality")
    )
    context = {"company": company, "cm_refers": cm_refers}
    return render(request, "customer/detail.html", context)


def update(request, customer_id):
    company = Company.objects.get(pk=customer_id)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        print(form)
        if form.is_valid():
            # form.id = customer_id
            form.save()
            print("form saved")
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


def new_contract(request, customer_id):
    if request.method == "POST":
        # Process the form data
        # Retrieve the data from the request.POST dictionary
        # Create a new contract object with the retrieved data
        # Save the contract object to the database
        # Redirect to a success page or render a success message
        pass
    else:
        # Render the form for creating a new contract
        return render(request, "customer/new_contract.html")


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
