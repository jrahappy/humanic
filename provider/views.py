# Create your views here.
from django.contrib.auth.models import User
from accounts.models import CustomUser, Profile
from customer.models import Company
from minibooks.models import ReportMaster, ReportMasterStat
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .forms import ProviderForm


def index(request):

    q = request.GET.get("q")
    if q:
        doctors = (
            CustomUser.objects.filter(
                Q(profile__real_name__icontains=q)
                | Q(profile__specialty2__icontains=q)
                | Q(profile__email__icontains=q)
                | Q(profile__cv3_id__icontains=q)
                | Q(profile__onpacs_id__icontains=q)
            )
            .filter(is_staff=False)
            .select_related("profile")
            .order_by("profile__real_name")
        )
    else:
        doctors = (
            CustomUser.objects.filter(is_staff=False)
            .select_related("profile")
            .order_by("-username")
        )
        # update_profile = Profile.objects.filter(specialty2="신경두경부").update(
        #     specialty2="신경두경"
        # )

    paginator = Paginator(doctors, 10)  # Show 10 doctors per page
    page = request.GET.get("page")

    try:
        doctors = paginator.page(page)
    except PageNotAnInteger:
        doctors = paginator.page(1)
    except EmptyPage:
        doctors = paginator.page(paginator.num_pages)

    context = {"doctors": doctors}
    return render(request, "provider/index.html", context)


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


def view_provider(request, id):
    provider = CustomUser.objects.select_related("profile").get(pk=id)
    rs = ReportMasterStat.objects.filter(provider=provider)

    rs_monthly = (
        rs.values("ayear", "amonth")
        .annotate(
            total_count_temp=Sum("total_count"),
            total_revenue_temp=Sum("total_revenue"),
        )
        .order_by("-ayear", "-amonth")
    )
    # print(rs_monthly)
    context = {"provider": provider, "rs_monthly": rs_monthly}

    return render(request, "provider/view_provider.html", context)


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
