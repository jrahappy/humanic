# Create your views here.
from accounts.models import (
    CustomUser,
    Profile,
    WorkHours,
    Holidays,
    ProductionTarget,
    HRFiles,
)
from accounts.forms import (
    HRFilesForm,
    ProductionTargetForm,
)
from referdex.forms import MatchRulesForm
from referdex.models import MatchRules, Team, TeamMember
from minibooks.models import ReportMasterStat
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from .forms import ProviderForm
from .filters import ProfileFilter
from django.contrib.auth.decorators import login_required
from utils.base_func import (
    get_amodality_choices,
    APPT_DAYS,
    HOLIDAY_CATEGORY,
    TERM_CATEGORY,
    WORKHOURS,
)
import json


@login_required
def index(request):
    user = request.user
    q = request.GET.get("q")
    if q:
        doctors = (
            Profile.objects.filter(
                Q(real_name__icontains=q)
                | Q(email__icontains=q)
                # | Q(user__is_staff=False)
                & Q(user__is_doctor=True)
            )
            .select_related("user")
            .annotate(user__hr_files_count=Count("user__hrfiles__id"))
            .order_by("real_name")
        )
        if doctors.count() == 1:
            return redirect("provider:view_provider", doctors[0].user.id)
    else:
        doctors = (
            Profile.objects.filter(user__is_doctor=True)
            .select_related("user")
            .annotate(hrfiles_count=Count("user__hrfiles"))
            .order_by("real_name")
        )

    profile_filter = ProfileFilter(request.GET, queryset=doctors)
    doctors = profile_filter.qs
    emails = doctors.values_list("email", flat=True).filter(~Q(email=None)).distinct()
    email_list = ", ".join(list(emails)).replace("'", "").strip()

    is_chief = TeamMember.objects.filter(provider=user, role="chief").exists()
    if is_chief:
        doctors = doctors.filter(specialty2=user.profile.specialty2)

    # print(doctors.query)
    paginator = Paginator(doctors, 15)  # Show 10 doctors per page
    page = request.GET.get("page")

    try:
        doctors = paginator.page(page)
    except PageNotAnInteger:
        doctors = paginator.page(1)
    except EmptyPage:
        doctors = paginator.page(paginator.num_pages)

    context = {
        "doctors": doctors,
        "emails": email_list,
        "filter": profile_filter,
        "q": q,
    }
    return render(request, "provider/index.html", context)


@login_required
def new_provider(request):
    form = ProviderForm()
    if request.method == "POST":
        form = ProviderForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.user = CustomUser.objects.create_user(
                username=form.cleaned_data["user"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["user"],
            )
            form.user.is_doctor = True
            form.user.save()
            form.save()
            messages.success(request, "Provider created successfully")
            return redirect("provider:index")
        else:
            messages.error(request, "Error creating provider")
    return render(request, "provider/new_provider.html")


@login_required
def view_provider(request, id):
    provider = CustomUser.objects.select_related("profile").get(pk=id)
    profile = provider.profile

    rs = ReportMasterStat.objects.filter(provider=provider)
    hr_files = HRFiles.objects.filter(user=provider)
    match_rules = MatchRules.objects.filter(provider=provider)

    week_days = APPT_DAYS
    workhours = WORKHOURS

    selected_workhours = WorkHours.objects.filter(user=provider).order_by(
        "work_weekday"
    )
    selected_workhours_dict = {
        item["work_weekday"]: item["work_hour"]
        for item in selected_workhours.values("work_weekday", "work_hour")
    }

    targets = ProductionTarget.objects.filter(user=provider).order_by(
        "work_weekday", "modality"
    )

    rs_monthly = (
        rs.values("ayear", "amonth", "adate")
        .annotate(
            total_count_temp=Sum("total_count"),
            total_revenue_temp=Sum("total_revenue"),
            tatal_expense_temp=Sum("total_expense"),
        )
        .order_by("-adate")
    )
    # print(rs_monthly)
    context = {
        "provider": provider,
        "rs_monthly": rs_monthly,
        "hr_files": hr_files,
        "week_days": week_days,
        "workhours": workhours,
        "selected_workhours_dict": selected_workhours_dict,
        "targets": targets,
        "match_rules": match_rules,
    }

    return render(request, "provider/view_provider.html", context)


@login_required
def edit_provider(request, id):
    provider = CustomUser.objects.select_related("profile").get(pk=id)
    form = ProviderForm(instance=provider.profile)
    if request.method == "POST":
        form = ProviderForm(request.POST, instance=provider.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Provider updated successfully")
            return redirect("provider:view_provider", provider.id)
        else:
            messages.error(request, "Error updating provider")
    return render(
        request, "provider/edit_provider.html", {"form": form, "provider": provider}
    )


@login_required
def edit(request, id):
    provider = CustomUser.objects.select_related("profile").get(pk=id)
    form = ProviderForm(instance=provider.profile)
    if request.method == "POST":
        form = ProviderForm(request.POST, instance=provider.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Provider updated successfully")
            return redirect("provider:view_provider", provider.id)
        else:
            messages.error(request, "Error updating provider")
    return render(request, "provider/edit.html", {"form": form, "provider": provider})


def partial_hr_files(request, id):
    provider = get_object_or_404(CustomUser, pk=id)
    hr_files = HRFiles.objects.filter(user=provider)
    context = {"hr_files": hr_files, "provider": provider}
    return render(request, "provider/hr_files.html", context)


def hr_file_upload(request, id):
    provider = get_object_or_404(CustomUser, pk=id)
    if request.method == "POST":
        form = HRFilesForm(request.POST, request.FILES)
        # print(form)
        if form.is_valid():
            files = request.FILES.getlist("file")
            for file in files:
                file_name = file.name
                HRFiles.objects.create(user=provider, file_name=file_name, file=file)
                print(file_name)

            # messages.success(request, "HR File uploaded successfully")
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "HRfilesChanged": None,
                            "showMessage": "File(s) Added.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            messages.error(request, "Error uploading HR File")
    else:
        form = HRFilesForm()

    return render(
        request, "provider/hr_file_upload.html", {"provider": provider, "form": form}
    )


def delete_hr_file(request, provider_id, file_id):
    provider = get_object_or_404(CustomUser, pk=provider_id)
    hr_file = get_object_or_404(HRFiles, pk=file_id)
    hr_file.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "HRfilesChanged": None,
                    "showMessage": "File Deleted.",
                }
            )
        },
    )


def match_rule_create(request, provider_id):
    provider = get_object_or_404(CustomUser, pk=provider_id)

    if request.method == "POST":
        form = MatchRulesForm(request.POST)
        if form.is_valid():
            match_rule = form.save(commit=False)
            match_rule.provider = provider
            match_rule.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "MatchRulesChanged": None,
                            "showMessage": "Match Rule Added.",
                        }
                    )
                },
            )

    else:
        form = MatchRulesForm()
        context = {"provider": provider, "form": form}
        return render(request, "provider/match_rule_create.html", context)
    return redirect("provider:view_provider", provider.id)
    # return render(request, "provider/match_rule_create.html", {"provider": provider})
