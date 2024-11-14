from django.shortcuts import render
from django.db.models import Sum, Q, Prefetch, OuterRef
from collections import defaultdict
from minibooks.models import MagamMaster, ReportMasterStat, ReportMaster
from accounts.models import CustomUser, ProductionTarget, Profile, WorkHours, Holidays
from datetime import date, datetime


# Create your views here.
# def index(request):
#     # Dictionary to store doctors grouped by subspecialty
#     selected_date = date.today()
#     selected_weekday = selected_date.weekday() + 1
#     current_hour = datetime.now().hour

#     print("오늘 요일", selected_weekday)

#     selected_providers = CustomUser.objects.filter(
#         is_doctor=True,
#         is_active=True,
#         profile__contract_status="A",
#     ).select_related("profile")

#     selected_providers = selected_providers.prefetch_related(
#         Prefetch(
#             "productiontarget_set",
#             queryset=ProductionTarget.objects.filter(
#                 work_weekday=selected_weekday,
#             ),
#         )
#     )

#     print("오늘 일하는 분들", selected_providers.count())

#     context = {
#         "selected_date": selected_date,
#         "selected_providers": selected_providers,
#     }
#     return render(request, "referdex/index.html", context)


def index(request):
    selected_date = date.today()
    selected_weekday = (
        selected_date.weekday() + 1
    )  # Weekday for filtering ProductionTarget and WorkHours
    current_hour = datetime.now().hour

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
    )

    # Group providers by specialty with additional data
    grouped_by_specialty = defaultdict(list)
    for provider in selected_providers:
        specialty_name = provider.profile.specialty2
        grouped_by_specialty[specialty_name].append(
            {
                "provider": provider,
                "real_name": provider.profile.real_name,
                "production_targets": provider.filtered_production_targets,
                "workhours": provider.filtered_workhours,
            }
        )

    context = {
        "selected_date": selected_date,
        "grouped_by_specialty": dict(grouped_by_specialty),
    }
    return render(request, "referdex/index.html", context)
