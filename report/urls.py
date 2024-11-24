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
        "report_period_month_table/<int:ayear>/<int:amonth>/",
        views.report_period_month_table,
        name="report_period_month_table",
    ),
    path(
        "report_period_month_radiologist/<int:ayear>/<int:amonth>/<int:radio>/",
        views.report_period_month_radiologist,
        name="report_period_month_radiologist",
    ),
    path(
        "report_period_month_radiologist_detail/<int:ayear>/<int:amonth>/<int:provider>/<str:company>/<str:amodality>/",
        views.report_period_month_radiologist_detail,
        name="report_period_month_radiologist_detail",
    ),
    path(
        "search/",
        views.partial_search_provider,
        name="search",
    ),
    path(
        "search_t/",
        views.partial_search_provider_t,
        name="search_t",
    ),
    path(
        "search_company/",
        views.partial_search_customer,
        name="search_company",
    ),
    path("report_customer/", views.report_customer, name="report_customer"),
    path(
        "report_customer_detail/<int:id>/",
        views.report_customer_detail,
        name="report_customer_detail",
    ),
    path(
        "partial_customer_month/<int:company_id>/",
        views.partial_customer_month,
        name="partial_customer_month",
    ),
    path(
        "csv/<int:company_id>/<str:adate>/",
        views.customer_month_csv,
        name="customer_month_csv",
    ),
    path(
        "customer_month_print/<int:company_id>/<str:adate>/",
        views.customer_month_print,
        name="customer_month_print",
    ),
    path("performance/", views.performance, name="performance"),
    # path(
    #     "performance_month/<int:ayear>/<int:amonth>/",
    #     views.partial_performance_month,
    #     name="partial_performance_month",
    # ),
    path(
        "partial_pivot_table_view/<int:ayear>/<int:amonth>/",
        views.partial_pivot_table_view,
        name="partial_pivot_table_view",
    ),
    path("accounting/", views.accounting, name="accounting"),
    path(
        "accounting_month/<int:ayear>/<int:amonth>/",
        views.accounting_month,
        name="accounting_month",
    ),
    path("chart/", views.chart, name="chart"),
    path("monthly_pro_cus/", views.monthly_pro_cus, name="monthly_pro_cus"),
    path(
        "report_pro_cus/<int:ayear>/<int:amonth>/",
        views.report_pro_cus,
        name="report_pro_cus",
    ),
    path(
        "partial_customer_by_month/<int:ayear>/<int:company>/",
        views.partial_customer_by_month,
        name="partial_customer_by_month",
    ),
    path(
        "partial_provider_by_month/<int:ayear>/<int:provider>/",
        views.partial_provider_by_month,
        name="partial_provider_by_month",
    ),
    path(
        "partial_provider_by_month_pivot/<int:ayear>/<int:amonth>/<int:provider>/",
        views.partial_provider_by_month_pivot,
        name="partial_provider_by_month_pivot",
    ),
    path("rads/", views.rad_by_subspecialty, name="rad_by_subspecialty"),
]
