from django.shortcuts import render
from django.db.models import Sum, Q, Prefetch, Func
from collections import defaultdict
from minibooks.models import MagamMaster, ReportMasterStat, ReportMaster
from accounts.models import CustomUser, ProductionTarget, Profile, WorkHours, Holidays
from datetime import date, datetime
from utils.base_func import get_specialty_choices


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
