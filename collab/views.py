from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import (
    Refers,
    ReferHistory,
    IllnessCode,
    ReferIllness,
    ReferTreatment,
    ReferSimpleDiagnosis,
    SimpleDiagnosis,
)
from .forms import ReferForm, CollabCompanyForm
from accounts.models import CustomUser, Profile
from customer.models import Company, CustomerContact
from customer.forms import CompanyForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tablib import Dataset
from .resources import IllnessCodeResource, SimpleDiagnosisResource
import json
import csv
import io
import datetime


def partial_illness_list(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    illnesses = ReferIllness.objects.filter(refer=refer_id)
    context = {"illnesses": illnesses, "draft_refer": refer}
    return render(request, "collab/partial_illness_list.html", context)


def delete_refer_illness(request, refer_illness_id):
    refer_illness = ReferIllness.objects.get(id=refer_illness_id)
    refer_illness.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "IllnessChanged": None,
                    "showMessage": "Illness deleted",
                }
            )
        },
    )


def create_refer_illness(request, refer_id, illness_id):
    refer = Refers.objects.get(id=refer_id)
    illness = IllnessCode.objects.get(id=illness_id)
    new_one = ReferIllness.objects.create(refer=refer, illness=illness)
    print(new_one)
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "IllnessChanged": None,
                    "showMessage": "Illness added",
                }
            )
        },
    )


def partial_illness_code_search(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    context = {"draft_refer": refer}

    return render(request, "collab/partial_illness_code_search.html", context)


def partial_illness_code_list(request, refer_id):
    q = request.GET.get("q")
    print(q)
    if q:
        illnesses = IllnessCode.objects.filter(
            name__icontains=q
        ) | IllnessCode.objects.filter(code__icontains=q)
        paginator = Paginator(illnesses, 20)  # Show 10 illnesses per page
        page = request.GET.get("page")
        try:
            illnesses = paginator.page(page)
        except PageNotAnInteger:
            illnesses = paginator.page(1)
        except EmptyPage:
            illnesses = paginator.page(paginator.num_pages)
    else:
        illnesses = IllnessCode.objects.all()[0:10]

    refer = Refers.objects.get(id=refer_id)
    context = {"illnesses": illnesses, "draft_refer": refer}

    return render(request, "collab/partial_illness_code_list.html", context)


def delete_simple_diagnosis(request, simple_id):

    refer_simple = ReferSimpleDiagnosis.objects.get(id=simple_id)
    refer_simple.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "SimpleDiagnosisChanged": None,
                    "showMessage": "Simple Diagnosis deleted",
                }
            )
        },
    )


def create_simple_diagnosis(request, refer_id, simple_id):
    refer_id = int(refer_id)
    simple_id = int(simple_id)
    print(refer_id, simple_id)
    refer = Refers.objects.get(id=refer_id)
    simple = SimpleDiagnosis.objects.get(id=simple_id)
    new_one = ReferSimpleDiagnosis.objects.create(refer=refer, diagnosis=simple)
    print(new_one)
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "SimpleDiagnosisChanged": None,
                    "showMessage": "Simple Diagnosis added",
                }
            )
        },
    )


def partial_simple_list(request, refer_id):
    print(refer_id)
    refer = Refers.objects.get(id=refer_id)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    print(simples.count())
    context = {"simples": simples, "draft_refer": refer}
    return render(request, "collab/partial_simple_list.html", context)


# def partial_simple_diagnosis_list(request, refer_id):
#     simples = SimpleDiagnosis.objects.all()
#     context = {"simples": simples, "refer_id": refer_id}
#     return render(request, "collab/partial_simple_diagnosis_list.html", context)


def partial_simple_diagnosis_list(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    sims = SimpleDiagnosis.objects.all().order_by("order")
    v_html = ""
    v_step = -1
    v_code = ""
    header_flag = False
    header2_flag = False
    header3_flag = False

    i = 0
    for sim in sims:
        temp_htmx = (
            "<div class='flex flex-row justify-between items-center w-full mb-1'>"
        )
        if sim.is_head:
            if sim.step == 0:
                temp_header = temp_htmx + f"<h3>{sim.code1}</h3>"
            elif sim.step == 1:
                temp_header = f"<h3 class='mt-4'>{sim.code1}</h3>"
                temp_header += temp_htmx + f"<p class='text-sm ps-2'>--{sim.code2}</p>"
            elif sim.step == 2:
                temp_header = f"<h3 class='mt-4'>{sim.code1}</h3>"
                temp_header += f"<p class='text-sm ps-2'>--{sim.code2}</p>"
                temp_header += (
                    temp_htmx + f"<p class='text-sm ps-2'>----{sim.code3}</p>"
                )
            else:
                temp_header = f"<h3 class='mt-4'>{sim.code1}</h3>"
                temp_header += f"<p class='text-sm ps-2'>--{sim.code2}</p>"
                temp_header += f"<p class='text-sm ps-2'>----{sim.code3}</p>"
                temp_header += (
                    temp_htmx + f"<p class='text-sm ps-2'>------{sim.code4}</p>"
                )

        else:

            if sim.step == 0:
                temp_header = temp_htmx + f"<p class='text-sm'>{sim.code1}</p>"
            elif sim.step == 1:
                temp_header = temp_htmx + f"<p class='text-sm ps-2'>--{sim.code2}</p>"
            elif sim.step == 2:
                temp_header = temp_htmx + f"<p class='text-sm ps-2'>----{sim.code3}</p>"
            else:
                temp_header = (
                    temp_htmx + f"<p class='text-sm ps-2'>------{sim.code4}</p>"
                )
        temp_header += (
            f"<a href='#' class='btn btn-xs btn-primary' "
            f"hx-target='#simple_diagonosis_list_box' "
            f"hx-get='/collabcreate_simple_diagnosis/{refer.id}/{sim.id}'>Add</a>"
        )

        temp_header += "</div>"
        # print(temp_header)
        v_step = sim.step
        v_html += temp_header
        i += 1

    return render(
        request, "collab/partial_simple_diagnosis_list.html", {"html": v_html}
    )


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


def simplecode_list(request):
    user = request.user
    user = CustomUser.objects.get(id=user.id)
    company = Company.objects.filter(customuser=user).first()

    simples = SimpleDiagnosis.objects.all()
    paginator = Paginator(simples, 10)  # Show 10 illnesses per page
    page = request.GET.get("page")
    try:
        illnesses = paginator.page(page)
    except PageNotAnInteger:
        illnesses = paginator.page(1)
    except EmptyPage:
        illnesses = paginator.page(paginator.num_pages)

    context = {"simples": simples, "company": company}
    return render(request, "collab/simplecode_list.html", context)


def simplecode_import(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()

    if request.method == "POST":
        simple_resource = SimpleDiagnosisResource()
        dataset = Dataset()
        new_simple = request.FILES["myfile"]

        print(new_simple)

        dataset.load(new_simple.read(), format="xlsx")
        result = simple_resource.import_data(dataset, dry_run=True)

        for row in result:
            for error in row.errors:
                print(error)
        if not result.has_errors():
            simple_resource.import_data(dataset, dry_run=False)
        else:
            print(result.errors)

        return redirect("collab:simplecode_list")

    else:

        context = {"company": company}
        return render(request, "collab/simplecode_import.html", context)


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
    # print(company)
    # refers = Refers.objects.all().order_by("-created_at")
    refers = Refers.objects.exclude(status="Draft").order_by("-created_at")

    # Draft refer를 무조건 하나 만들어둔다.
    draft_exists = Refers.objects.filter(company=company, status="Draft").exists()
    print(draft_exists)
    if not draft_exists:
        # referred_date = datetime.date.today()
        Refers.objects.create(
            company=company,
            status="Draft",
            # referred_date=referred_date,
            # patient_birthdate=patient_birthdate,
        )
        print("Draft refer created")

    context = {"refers": refers, "company": company, "draft_exist": draft_exists}
    return render(request, "collab/index.html", context)


def refer_list(request, company_id):
    company = Company.objects.get(id=company_id)
    refers = Refers.objects.filter(company=company).order_by("-created_at")

    context = {"refers": refers, "company": company}
    return render(request, "collab/refer_list.html", context)


# def partial_simple_list(request):
#     refer_simples = ReferSimpleDiagnosis.objects.filter(refer=refer_id)
#     context = {"refer_simples": refer_simples}
#     return render(request, "collab/partial_simple_list.html", context)


def refer_create(request):
    user = request.user
    company = Company.objects.filter(customuser=user).first()
    draft_refer = Refers.objects.filter(company=company, status="Draft").first()
    simples = ReferSimpleDiagnosis.objects.filter(refer=draft_refer)
    simples.delete()
    illnesses = ReferIllness.objects.filter(refer=draft_refer)
    illnesses.delete()

    # print(draft_refer.id)
    if request.method == "POST":
        form = ReferForm(request.POST, instance=draft_refer)
        print("valid form?")
        if form.is_valid():
            form.save(commit=False)
            form.instance.company = company
            form.instance.status = "Requested"
            form.save()
            return redirect("collab:refer_detail", refer_id=draft_refer.id)
        else:
            print(form.errors)
            context = {
                "form": form,
                "company": company,
                "draft_refer": draft_refer,
                "simples": simples,
                "illnesses": illnesses,
            }
            return render(request, "collab/refer_create.html", context)
    else:
        form = ReferForm(instance=draft_refer)
        context = {
            "form": form,
            "company": company,
            "draft_refer": draft_refer,
            "simples": simples,
            "illnesses": illnesses,
        }
        return render(request, "collab/refer_create.html", context)


def refer_detail(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    history = ReferHistory.objects.filter(refer=refer)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    illnesses = ReferIllness.objects.filter(refer=refer)
    context = {
        "refer": refer,
        "simples": simples,
        "illnesses": illnesses,
        "company": company,
        "history": history,
    }
    return render(request, "collab/refer_detail.html", context)


def refer_print(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    company = refer.company
    history = ReferHistory.objects.filter(refer=refer)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    illnesses = ReferIllness.objects.filter(refer=refer)
    context = {
        "refer": refer,
        "simples": simples,
        "illnesses": illnesses,
        "company": company,
        "history": history,
    }
    return render(request, "collab/refer_print.html", context)


def refer_update(request, refer_id):
    draft_refer = Refers.objects.get(id=refer_id)
    company = draft_refer.company
    simples = ReferSimpleDiagnosis.objects.filter(refer=draft_refer)
    illnesses = ReferIllness.objects.filter(refer=draft_refer)

    # print(draft_refer.id)
    if request.method == "POST":
        form = ReferForm(request.POST, instance=draft_refer)
        print("valid form?")
        if form.is_valid():
            form.save(commit=False)
            form.instance.company = company
            form.instance.status = "Requested"
            form.save()
            return redirect("collab:refer_detail", refer_id=draft_refer.id)
        else:
            print(form.errors)
            context = {
                "form": form,
                "company": company,
                "draft_refer": draft_refer,
                "simples": simples,
                "illnesses": illnesses,
            }
            return render(request, "collab/refer_update.html", context)
    else:
        form = ReferForm(instance=draft_refer)
        context = {
            "form": form,
            "company": company,
            "draft_refer": draft_refer,
            "simples": simples,
            "illnesses": illnesses,
        }
        return render(request, "collab/refer_update.html", context)


def refer_delete(request, refer_id):
    refer = Refers.objects.get(id=refer_id)
    refer_simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    refer_simples.delete()
    refer_illnesses = ReferIllness.objects.filter(refer=refer)
    refer_illnesses.delete()
    refer.delete()
    return redirect("collab:index")


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
