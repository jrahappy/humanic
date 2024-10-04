from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("partial_dashboard", views.partial_dashboard, name="partial_dashboard"),
    path("profile", views.profile, name="profile"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("stat", views.stat, name="stat"),
    path(
        "report_period_month_radiologist/<int:ayear>/<int:amonth>/<int:radio>/",
        views.report_period_month_radiologist,
        name="report_period_month_radiologist",
    ),
    path("daisyui/", views.daisyui, name="daisyui"),
]
