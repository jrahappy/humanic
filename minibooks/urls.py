from django.urls import path
from . import views

app_name = "minibooks"
urlpatterns = [
    path("", views.index, name="index"),
    path("history_delete/<int:id>/", views.history_delete, name="history_delete"),
    path("new_upload", views.new_upload, name="new_upload"),
    path(
        "create_reportmaster/<int:id>/",
        views.create_reportmaster,
        name="create_reportmaster",
    ),
    path(
        "snippet_reportmaster/<int:id>/",
        views.snippet_reportmaster,
        name="snippet_reportmaster",
    ),
    path("dry_run/<int:id>/", views.dry_run, name="dry_run"),
    path("clean_data/<int:id>/", views.clean_data, name="clean_data"),
    path("current_progress/<int:id>/", views.current_progress, name="current_progress"),
    path("get_progress/<int:id>/", views.get_progress, name="get_progress"),
    path(
        "aggregate_data/<int:upload_history_id>/",
        views.aggregate_data,
        name="aggregate_data",
    ),
    path(
        "aggregate_data_result/<int:upload_history_id>/",
        views.aggregate_data_result,
        name="aggregate_data_result",
    ),
    path("agg_detail/<int:id>/", views.agg_detail, name="agg_detail"),
    path("partial_tracking/<int:id>/", views.partial_tracking, name="partial_tracking"),
    path("magam/", views.magam_list, name="magam_list"),
    path("magam/new/", views.magam_new, name="magam_new"),
    path("re_cal_magam/<int:id>/", views.re_cal_magam, name="re_cal_magam"),
    path("magam/view/<int:id>/", views.magam_view, name="magam_view"),
    path(
        "magam/apply_rule/<int:magam_id>/<int:rule_id>/",
        views.apply_rule,
        name="apply_rule",
    ),
    path(
        "magam/apply_rule_progress/<int:magam_id>/<int:rule_id>/",
        views.apply_rule_progress,
        name="apply_rule_progress",
    ),
    path(
        "magam/apply_rule_progress_check/<int:magam_id>/<int:rule_id>/",
        views.apply_rule_progress_check,
        name="apply_rule_progress_check",
    ),
    path(
        "magam/recalc/<str:ayear>/<str:amonth>/<int:provider_id>/",
        views.re_calc_share,
        name="re_calc_share",
    ),
    path("get_open/<int:id>/<str:is_opened>/", views.get_open, name="get_open"),
]
