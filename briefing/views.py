from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django_pivot.pivot import pivot
from django_pivot.histogram import histogram

# from importdata.models import rawdata, UploadHistory
from minibooks.models import UploadHistory, ReportMaster
from utils.models import ChoiceMaster
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser, Profile
from datetime import date


@login_required
def index(request):

    providers = CustomUser.objects.filter(is_doctor=True).order_by("username")
    selected_provider = request.GET.get("provider", None)

    ayears = ChoiceMaster.objects.filter(choice_name="AYEAR").order_by("choice_order")
    selected_ayear = request.GET.get("ayear", None)
    if not selected_ayear:
        selected_ayear = date.today().year

    amonths = ChoiceMaster.objects.filter(choice_name="AMONTH").order_by("choice_order")
    selected_amonth = request.GET.get("amonth", None)
    if not selected_amonth:
        selected_amonth = date.today().month

    # print(radiologist)
    # if radiologist:
    #     aggregation_data = (
    #         ReportMaster.objects.filter(
    #             ayear=selected_ayear, amonth=selected_amonth, radiologist=radiologist
    #         )
    #         # .values("apptitle", "equipment")
    #         .values("apptitle").annotate(
    #             total_price=Sum("readprice"),
    #             average_price=Avg("readprice"),
    #             total_cases=Count("case_id"),
    #         )
    #     )
    #     agg_data = ReportMaster.objects.filter(
    #         ayear=selected_ayear, amonth=selected_amonth, radiologist=radiologist
    #     ).aggregate(
    #         total_price=Sum("readprice"),
    #         average_price=Avg("readprice"),
    #         total_cases=Count("case_id"),
    #     )
    # else:
    #     aggregation_data = ReportMaster.objects.filter(
    #         ayear=selected_ayear, amonth=selected_amonth, radiologist=radiologist
    #     ).aggregate(
    #         total_price=Sum("readprice"),
    #         average_price=Avg("readprice"),
    #         total_cases=Count("case_id"),
    #     )
    #     agg_data = aggregation_data

    context = {
        # "pivot_data": pivot_data,
        "providers": providers,
        "selected_provider": selected_provider,
        # "aggregation_data": aggregation_data,
        # "agg_data": agg_data,
        "selected_ayear": selected_ayear,
        "ayears": ayears,
        "selected_amonth": selected_amonth,
        "amonths": amonths,
    }
    print(selected_ayear, selected_amonth, selected_provider)
    # print(aggregation_data)
    return render(request, "briefing/index.html", context)
