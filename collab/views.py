from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Refers, ReferHistory, IllnessCode, ReferIllness, ReferTreatment
from .forms import ReferForm, CollabCompanyForm
from accounts.models import CustomUser, Profile
from customer.models import Company, CustomerContact
from customer.forms import CompanyForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tablib import Dataset
from .resources import IllnessCodeResource
import json
import csv
import io


def illness_list(request):
    user = request.user
    user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    illnesses = IllnessCode.objects.all()
    paginator = Paginator(illnesses, 10)  # Show 10 illnesses per page
    page = request.GET.get("page")
    try:
        illnesses = paginator.page(page)
    except PageNotAnInteger:
        illnesses = paginator.page(1)
    except EmptyPage:
        illnesses = paginator.page(paginator.num_pages)

    context = {"illnesses": illnesses, "company": company}
    return render(request, "collab/illness_list.html", context)


def illness_code_import(request):
    user = request.user
    # user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    if request.method == "POST":
        illness_resource = IllnessCodeResource()
        dataset = Dataset()
        new_illness = request.FILES["myfile"]
        print(new_illness)

        dataset.load(new_illness.read(), format="xlsx")
        result = illness_resource.import_data(dataset, dry_run=True)

        for row in result:
            for error in row.errors:
                print(error)

        if not result.has_errors():
            illness_resource.import_data(dataset, dry_run=False)
        else:
            print(result.errors)

        return redirect("collab:illness_list")

    else:
        context = {"company": company}
        return render(request, "collab/illness_code_import.html", context)


def home(request):
    user = request.user
    refers = Refers.objects.all().order_by("-created_at")
    paginator = Paginator(refers, 10)  # Show 10 refers per page
    page = request.GET.get("page")
    try:
        refers = paginator.page(page)
    except PageNotAnInteger:
        refers = paginator.page(1)
    except EmptyPage:
        refers = paginator.page(paginator.num_pages)
    context = {"refers": refers}
    return render(request, "collab/home.html", context)


def index(request):
    user = request.user
    user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()
    print(company)
    refers = Refers.objects.all().order_by("-created_at")
    context = {"refers": refers, "company": company}
    return render(request, "collab/index.html", context)


def refer_list(request, company_id):
    company = Company.objects.get(id=company_id)
    refers = Refers.objects.filter(company=company).order_by("-created_at")
    context = {"refers": refers, "company": company}
    return render(request, "collab/refer_list.html", context)


def refer_create(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    print(company)
    if request.method == "POST":
        form = ReferForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.company = company
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "RefersChanged": None,
                            "showMessage": "Refer added",
                        }
                    )
                },
            )
        else:
            print(form.errors)
    else:
        form = ReferForm()
        context = {"form": form, "company": company}
    return render(request, "collab/refer_create.html", context)


def refer_detail(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    history = ReferHistory.objects.filter(refer=refer)
    context = {"refer": refer, "history": history, "company": company}
    return render(request, "collab/refer_detail.html", context)


def refer_update(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    history = ReferHistory.objects.filter(refer=refer)
    if request.method == "POST":
        form = ReferForm(request.POST, instance=refer)
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "RefersChanged": None,
                            "showMessage": "Refer added",
                        }
                    )
                },
            )
    else:
        form = ReferForm(instance=refer)
    context = {"refer": refer, "history": history, "company": company, "form": form}
    return render(request, "collab/refer_update.html", context)


def company_info(request, company_id):
    company = Company.objects.get(id=company_id)
    contacts = CustomerContact.objects.filter(company=company)
    # refers = Refers.objects.filter(company=company)
    context = {"company": company, "contacts": contacts}
    return render(request, "collab/company_info.html", context)


def company_update(request, company_id):
    company = Company.objects.get(id=company_id)
    contacts = CustomerContact.objects.filter(company=company)
    if request.method == "POST":
        form = CollabCompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("collab:company_info", company_id=company.id)

    else:
        form = CollabCompanyForm(instance=company)

    context = {"company": company, "contacts": contacts, "form": form}
    return render(request, "collab/company_update.html", context)


def profile(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    profile = Profile.objects.filter(user=user).first()
    context = {"profile": profile, "company": company}
    return render(request, "collab/profile.html", context)
