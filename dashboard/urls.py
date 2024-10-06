from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("partial_dashboard", views.partial_dashboard, name="partial_dashboard"),
    path("profile", views.profile, name="profile"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("stat", views.stat, name="stat"),
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
        "password/change/",
        views.password_change,
        name="change_password",
    ),
    path(
        "password/change/done/", views.password_change_done, name="password_change_done"
    ),
    path("daisyui/", views.daisyui, name="daisyui"),
]
