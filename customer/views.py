from django.shortcuts import render
from .models import Company, Contract, ContractItem, Product, Platform
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
    # Retrieve the customer object from the database
    # Pass the customer object to the template for rendering
    company = Company.objects.get(pk=customer_id)
    # referred = cleanData.objects.filter(apptitle=company.business_name)
    # context = {"company": company, "referred": referred}
    context = {"company": company}
    return render(request, "customer/detail.html", context)


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
