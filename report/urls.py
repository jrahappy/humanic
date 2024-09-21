from django.urls import path
from . import views

app_name = "report"
urlpatterns = [
    path("", views.index, name="index"),
    path("report_period/", views.report_period, name="report_period"),
    path(
        "report_period_month/<int:ayear>/<int:amonth>/",
        views.report_period_month,
        name="report_period_month",
    ),
    path(
        "report_period_month_radiologist/<int:ayear>/<int:amonth>/<str:radio>/",
        views.report_period_month_radiologist,
        name="report_period_month_radiologist",
    ),
]
