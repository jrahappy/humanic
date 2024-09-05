from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django_pivot.pivot import pivot
from django_pivot.histogram import histogram
from importdata.models import rawdata, importhistory


# Create your views here.
def index(request):

    radiologists = (
        rawdata.objects.filter(importhistory=10)
        .values_list("radiologist", flat=True)
        .distinct()
    )

    radiologist = request.GET.get("radiologist", None)
    print(radiologist)
    if radiologist:
        aggregation_data = (
            rawdata.objects.filter(importhistory=10, radiologist=radiologist)
            .values("apptitle", "equipment")
            .annotate(
                total_price=Sum("readprice"),
                average_price=Avg("readprice"),
                total_cases=Count("case_id"),
            )
        )
        agg_data = rawdata.objects.filter(
            importhistory=6, radiologist=radiologist
        ).aggregate(
            total_price=Sum("readprice"),
            average_price=Avg("readprice"),
            total_cases=Count("case_id"),
        )
    else:
        aggregation_data = rawdata.objects.filter(importhistory=6).aggregate(
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
