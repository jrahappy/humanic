from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, Prefetch, Func, Value
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from collections import defaultdict
from datetime import timedelta, date, datetime
from minibooks.models import MagamMaster, ReportMasterStat, ReportMaster
from accounts.models import CustomUser, ProductionTarget, Profile, WorkHours, Holidays
from utils.base_func import get_specialty_choices
from .models import ProductionMade, ProductionMadeDetail
from .forms import ProductionMadeForm, ProductionMadeDetailForm
from django.http import HttpResponse
from django.utils import timezone
import json


def index(request):
    selected_date = request.GET.get("date-picker")
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        selected_date = date.today()
    print("Selected Date: ", selected_date)
    selected_weekday = (
        selected_date.weekday() + 1
    )  # Weekday for filtering ProductionTarget and WorkHours
    current_hour = datetime.now().hour

    ko_kr = Func(
        "profile__specialty2",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )

    # Filter doctors who are active and contracted
    selected_providers = (
        CustomUser.objects.filter(
            Q(profile__contract_status="A") | Q(profile__contract_status="P"),
            is_doctor=True,
            is_active=True,
        )  # Load related profile data
        .select_related("profile")
        .prefetch_related(
            Prefetch(
                "productiontarget_set",
                queryset=ProductionTarget.objects.filter(work_weekday=selected_weekday),
                to_attr="filtered_production_targets",
            ),
            Prefetch(
                "workhours_set",
                queryset=WorkHours.objects.filter(work_weekday=selected_weekday),
                to_attr="filtered_workhours",
            ),
        )
        .order_by(ko_kr.asc())
    )

    stat_values = defaultdict(dict)
    specialties = sorted(get_specialty_choices())

    total_provider_a = CustomUser.objects.filter(
        is_doctor=True,
        is_active=True,
        profile__contract_status="A",
        workhours__work_weekday=selected_weekday,
    ).count()
    total_provider_p = CustomUser.objects.filter(
        is_doctor=True,
        is_active=True,
        profile__contract_status="P",
        workhours__work_weekday=selected_weekday,
    ).count()

    for spct in specialties:
        specialty_name = spct[0]
        # print("Specialty Name: ", specialty_name)
        # Active providers by specialty
        count_provider_a = CustomUser.objects.filter(
            profile__specialty2=specialty_name,
            is_doctor=True,
            is_active=True,
            profile__contract_status="A",
            workhours__work_weekday=selected_weekday,
        ).count()
        # PartTime providers by specialty
        count_provider_p = CustomUser.objects.filter(
            profile__specialty2=specialty_name,
            is_doctor=True,
            is_active=True,
            profile__contract_status="P",
            workhours__work_weekday=selected_weekday,
        ).count()

        # Total CT 희망 갯수 합계
        sum_ct_target = (
            ProductionTarget.objects.filter(
                work_weekday=selected_weekday,
                modality="ct",
                user__profile__specialty2=specialty_name,
                user__is_doctor=True,
                user__is_active=True,
            ).aggregate(Sum("target_value"))["target_value__sum"]
            or 0
        )

        sum_mr_target = (
            ProductionTarget.objects.filter(
                work_weekday=selected_weekday,
                modality="mr",
                user__profile__specialty2=specialty_name,
                user__is_doctor=True,
                user__is_active=True,
            ).aggregate(Sum("target_value"))["target_value__sum"]
            or 0
        )

        sum_mg_target = (
            ProductionTarget.objects.filter(
                work_weekday=selected_weekday,
                modality="mg",
                user__profile__specialty2=specialty_name,
                user__is_doctor=True,
                user__is_active=True,
            ).aggregate(Sum("target_value"))["target_value__sum"]
            or 0
        )

        sum_cr_target = (
            ProductionTarget.objects.filter(
                work_weekday=selected_weekday,
                modality="cr",
                user__profile__specialty2=specialty_name,
                user__is_doctor=True,
                user__is_active=True,
            ).aggregate(Sum("target_value"))["target_value__sum"]
            or 0
        )

        stat_values[specialty_name] = {
            "count_provider_a": count_provider_a,
            "count_provider_p": count_provider_p,
            "sum_ct_target": sum_ct_target,
            "sum_mr_target": sum_mr_target,
            "sum_mg_target": sum_mg_target,
            "sum_cr_target": sum_cr_target,
        }

    # Group providers by specialty with additional data
    grouped_by_specialty = defaultdict(list)
    for provider in selected_providers:
        specialty_name = provider.profile.specialty2
        grouped_by_specialty[specialty_name].append(
            {
                "provider": provider,
                "iid": provider.id,
                "real_name": provider.profile.real_name,
                "contract_status": provider.profile.contract_status,
                "production_targets": provider.filtered_production_targets,
                "workhours": provider.filtered_workhours,
            }
        )

    context = {
        "today": selected_date,
        "total_provider_a": total_provider_a,
        "total_provider_p": total_provider_p,
        "selected_date": selected_date,
        "grouped_by_specialty": dict(grouped_by_specialty),
        "stat_values": dict(stat_values),
    }
    return render(request, "referdex/index.html", context)


def pm(request):
    pms = (
        ProductionMade.objects.filter()
        .prefetch_related("details")
        .order_by("-created_at")
    )

    # Annotate each ProductionMade instance with the sum of assigned_qty, handling None values
    pms_annotated = pms.annotate(
        total_assigned_qty=Coalesce(Sum("details__assigned_qty"), Value(0))
    )

    # Calculate the total sum of assigned_qty across all ProductionMade instances
    total_assigned_qty = (
        pms_annotated.aggregate(total_qty=Sum("total_assigned_qty"))["total_qty"] or 0
    )

    # Add pagination
    paginator = Paginator(pms_annotated, 10)  # Show 10 items per page
    page = request.GET.get("page")
    try:
        pm_list = paginator.page(page)
    except PageNotAnInteger:
        pm_list = paginator.page(1)
    except EmptyPage:
        pm_list = paginator.page(paginator.num_pages)

    context = {
        "pm_list": pm_list,
        "total_assigned_qty": total_assigned_qty,
    }

    return render(request, "referdex/pm.html", context)


def partial_pm(request):

    pms = (
        ProductionMade.objects.filter()
        .prefetch_related("details")
        .order_by("-created_at")
    )

    # Annotate each ProductionMade instance with the sum of assigned_qty, handling None values
    pms_annotated = pms.annotate(
        total_assigned_qty=Coalesce(Sum("details__assigned_qty"), Value(0))
    )

    # Calculate the total sum of assigned_qty across all ProductionMade instances
    total_assigned_qty = (
        pms_annotated.aggregate(total_qty=Sum("total_assigned_qty"))["total_qty"] or 0
    )

    # Add pagination
    paginator = Paginator(pms_annotated, 10)  # Show 10 items per page
    page = request.GET.get("page")
    try:
        pm_list = paginator.page(page)
    except PageNotAnInteger:
        pm_list = paginator.page(1)
    except EmptyPage:
        pm_list = paginator.page(paginator.num_pages)

    context = {
        "pm_list": pm_list,
        "total_assigned_qty": total_assigned_qty,
    }

    return render(request, "referdex/partial_pm.html", context)


def pm_delete(request, pm_id):
    pm = ProductionMade.objects.get(id=pm_id)
    pm.delete()

    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "PMListChanged": None,
                    "showMessage": "Request was deleted.",
                }
            )
        },
    )


def pm_detail(request, pm_id):
    # Retrieve the ProductionMade instance
    pm = get_object_or_404(ProductionMade, id=pm_id)
    # 요청된 갯수
    requested_qty = pm.requested_qty

    # Retrieve related ProductionMadeDetail instances
    pmds = ProductionMadeDetail.objects.filter(production=pm)
    # 현재 pm에 할당된 총 갯수
    pmds_total = pmds.aggregate(Sum("assigned_qty"))["assigned_qty__sum"] or 0

    available_qty = requested_qty - pmds_total

    if available_qty <= 0:
        available_qty = 0
        this_pm = ProductionMade.objects.get(id=pm_id)
        this_pm.is_completed = True
        this_pm.save()
    else:
        available_qty = available_qty

    # Determine the selected date and weekday
    selected_date_str = request.GET.get("date-picker", "")
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()
    selected_weekday = (
        selected_date.weekday() + 1
    )  # Monday is 0 in Python; adjust to match your model

    # Retrieve providers matching the specialty and contract status
    providers = CustomUser.objects.filter(
        Q(profile__contract_status="A") | Q(profile__contract_status="P"),
        is_doctor=True,
        is_active=True,
        profile__specialty2=pm.specialty2,
        productiontarget__modality=pm.modality,
        productiontarget__work_weekday=selected_weekday,
    ).select_related("profile")

    # Prefetch related ProductionTarget and WorkHours for the selected weekday
    providers = providers.prefetch_related(
        Prefetch(
            "productiontarget_set",
            queryset=ProductionTarget.objects.filter(work_weekday=selected_weekday),
            to_attr="filtered_production_targets",
        ),
        Prefetch(
            "workhours_set",
            queryset=WorkHours.objects.filter(work_weekday=selected_weekday),
            to_attr="filtered_workhours",
        ),
    )

    # Aggregate assigned quantities for each provider on the selected date
    assigned_quantities = (
        ProductionMadeDetail.objects.filter(
            # created_at__date=selected_date, production=pm
            created_at__date=selected_date
        )
        # .values("provider", "production")
        .values("provider").annotate(total_assigned_qty=Sum("assigned_qty"))
    )

    # Create a mapping of provider IDs to their assigned quantities
    assigned_qty_map = {
        item["provider"]: item["total_assigned_qty"] for item in assigned_quantities
    }

    # Group providers by specialty and include relevant data
    grouped_by_specialty_for_request = defaultdict(list)
    for provider in providers:
        specialty_name = provider.profile.specialty2
        grouped_by_specialty_for_request[specialty_name].append(
            {
                "provider": provider,
                "iid": provider.id,
                "real_name": provider.profile.real_name,
                "contract_status": provider.profile.contract_status,
                "production_targets": provider.filtered_production_targets,
                "production_made": assigned_qty_map.get(provider.id, 0),
                "workhours": provider.filtered_workhours,
            }
        )

    pmd_form = ProductionMadeDetailForm()
    context = {
        "pm": pm,
        "pmds": pmds,
        "pmds_total": pmds_total,
        "available_qty": available_qty,
        "selected_modality": pm.modality,
        "grouped_by_specialty_for_request": dict(grouped_by_specialty_for_request),
        "pmd_form": pmd_form,
    }
    return render(request, "referdex/pm_detail.html", context)


def pmd_list_by_provider(request, pm_id, provider_id):
    pm = ProductionMade.objects.get(id=pm_id)
    provider = CustomUser.objects.get(id=provider_id)
    real_name = provider.profile.real_name
    pmds = ProductionMadeDetail.objects.filter(
        # provider=provider, created_at__date=pm.created_at.date()
        provider=provider,
        created_at__date=timezone.now().date(),
    )
    selected_date = timezone.now().date()
    context = {
        "pm": pm,
        "provider": provider,
        "real_name": real_name,
        "selected_date": selected_date,
        "pmds": pmds,
    }
    return render(request, "referdex/partial_pmd_list_by_provider.html", context)


def pmds(request, pm_id):
    pm = ProductionMade.objects.get(id=pm_id)
    pmds = ProductionMadeDetail.objects.filter(production=pm)
    context = {
        "pm": pm,
        "pmds": pmds,
    }
    return render(request, "referdex/partical_pmds.html", context)


def pm_assign(request, pm_id, provider_id, modality):
    pm = get_object_or_404(ProductionMade, id=pm_id)
    provider = get_object_or_404(CustomUser, id=provider_id)

    # 요청된 갯수
    requested_qty = pm.requested_qty
    # Retrieve related ProductionMadeDetail instances
    pmds = ProductionMadeDetail.objects.filter(production=pm)
    # 현재 pm에 할당된 총 갯수
    pmds_total = pmds.aggregate(Sum("assigned_qty"))["assigned_qty__sum"] or 0
    available_qty = requested_qty - pmds_total

    if request.method == "POST":
        form = ProductionMadeDetailForm(request.POST)
        if form.is_valid():
            assigned_qty = form.cleaned_data["assigned_qty"]
            # 초과량을 할당할 수 없음(중요)
            if assigned_qty >= available_qty:
                assigned_qty = available_qty
                # pm의 is_completed를 True로 변경
                is_completed = True
                pm.is_completed = True
                pm.save()
            else:
                is_completed = False
                pm.is_completed = False
                pm.save()

            is_exist = ProductionMadeDetail.objects.filter(
                provider=provider, production=pm
            ).exists()

            if is_exist:
                pm_detail = ProductionMadeDetail.objects.get(
                    provider=provider, production=pm
                )
                pm_detail.assigned_qty = assigned_qty
                pm_detail.save()
            else:
                pm_detail = ProductionMadeDetail.objects.create(
                    production=pm,
                    provider=provider,
                    modality=modality,
                    assigned_qty=assigned_qty,
                )

            return redirect("referdex:pm_detail", pm_id=pm_id)
        else:
            print(form.errors)
            return redirect("referdex:pm_detail", pm_id=pm_id)
    else:
        print("not post")
        return redirect("referdex:pm_detail", pm_id=pm_id)


def pmd_delete(request, pmd_id):
    pmd = ProductionMadeDetail.objects.get(id=pmd_id)
    pm = pmd.production
    pm.is_completed = False
    pm.save()
    pmd.delete()

    return redirect("referdex:pm_detail", pm_id=pmd.production.id)


def pm_create(request):
    if request.method == "POST":
        form = ProductionMadeForm(request.POST)
        if form.is_valid():
            pm = form.save(commit=False)
            pm.created_by = request.user
            pm.save()
            return redirect("referdex:pm")
        else:
            print(form.errors)
    else:
        form = ProductionMadeForm()
    context = {
        "form": form,
        "user": request.user,
    }
    return render(request, "referdex/pm_create.html", context)


def pm_edit(request, pm_id):
    pm = ProductionMade.objects.get(id=pm_id)
    is_completed = pm.is_completed
    if request.method == "POST":
        form = ProductionMadeForm(request.POST, instance=pm)
        if form.is_valid():
            pm = form.save(commit=False)
            pm.save()
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "PMListChanged": None,
                            "showMessage": "Request was changed.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
    else:
        form = ProductionMadeForm(instance=pm)
    context = {
        "form": form,
        "pm": pm,
        "pm_id": pm_id,
        "user": request.user,
        "is_completed": is_completed,
    }
    print("pm_id: ", pm_id)
    return render(request, "referdex/pm_edit.html", context)
