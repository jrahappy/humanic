from django.urls import path
from . import views


app_name = "cust"
urlpatterns = [
    path("", views.index, name="index"),
    path("stat/", views.stat, name="stat"),
    path(
        "report_period_month_company/<int:ayear>/<int:amonth>/<int:company_id>/",
        views.report_period_month_company,
        name="report_period_month_company",
    ),
    path(
        "report_period_month_company_detail/<int:ayear>/<int:amonth>/<str:provider>/<int:company>/<str:amodality>/",
        views.report_period_month_company_detail,
        name="report_period_month_company_detail",
    ),
    path("partial_dashboard", views.partial_dashboard, name="partial_dashboard"),
    #
    # path("signup/", views.signup, name="signup"),
    # path("user_update/", views.user_update, name="user_update"),
    # path("password_change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
]
