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
    path("board/", views.board, name="board"),
    path("detail/<int:pk>/", views.detail, name="detail"),
    path("wh/", views.workhours, name="workhours"),
    path("wh/create/<int:id>/", views.workhour_create, name="workhour_create"),
    path("wh/remove/<int:id>/", views.workhour_remove, name="workhour_remove"),
    path("holy/create/", views.holiday_create, name="holiday_create"),
    path("holy/remove/", views.holiday_remove, name="holiday_remove"),
    path(
        "wh/modality/target/create/<int:id>/",
        views.create_weekday_modality_target,
        name="create_weekday_modality_target",
    ),
    path(
        "wh/modality/target/list/<int:id>/",
        views.weekday_modality_targets,
        name="weekday_modality_targets",
    ),
    path(
        "wh/modality/target/remove/<int:id>/",
        views.delete_weekday_modality_target,
        name="delete_weekday_modality_target",
    ),
    path(
        "export_csv_provider/<int:ayear>/<int:amonth>/<int:provider_id>/",
        views.export_csv_provider,
        name="export_csv_provider",
    ),
]
