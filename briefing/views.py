from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django_pivot.pivot import pivot
from django_pivot.histogram import histogram
from importdata.models import rawdata, importhistory
from minibooks.models import UploadHistory, ReportMaster
from django.contrib.auth.decorators import login_required


@login_required
def index(request):

    radiologists = (
        rawdata.objects.filter(importhistory=2)
        .values_list("radiologist", flat=True)
        .distinct()
    )

    radiologist = request.GET.get("radiologist", None)
    print(radiologist)
    if radiologist:
        aggregation_data = (
            rawdata.objects.filter(importhistory=2, radiologist=radiologist)
            # .values("apptitle", "equipment")
            .values("apptitle").annotate(
                total_price=Sum("readprice"),
                average_price=Avg("readprice"),
                total_cases=Count("case_id"),
            )
        ).order_by("apptitle")
        agg_data = (
            rawdata.objects.filter(importhistory=2, radiologist=radiologist)
            .aggregate(
                total_price=Sum("readprice"),
                average_price=Avg("readprice"),
                total_cases=Count("case_id"),
            )
            .order_by("apptitle", "equipment")
        )
    else:
        aggregation_data = rawdata.objects.filter(importhistory=2).aggregate(
            total_price=Sum("readprice"),
            average_price=Avg("readprice"),
            total_cases=Count("case_id"),
        )
        agg_data = aggregation_data

    context = {
        # "pivot_data": pivot_data,
        "radiologists": radiologists,
        "selected_radiologist": radiologist,
        "aggregation_data": aggregation_data,
        "agg_data": agg_data,
    }
    # print(aggregation_data)
    return render(request, "briefing/index.html", context)
