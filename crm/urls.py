from django.urls import path
from . import views

app_name = "crm"
urlpatterns = [
    path("", views.index, name="index"),
    path("new_opp/<int:company_id>/", views.new_opp, name="new_opp"),
    path("opps_customer/<int:company_id>/", views.opps_customer, name="opps_customer"),
    path("edit_opp/<int:opp_id>/", views.edit_opp, name="edit_opp"),
    path("delete_opp/<int:opp_id>/", views.delete_opp, name="delete_opp"),
    path("chances/", views.chances, name="chances"),
    path("new_chance/", views.new_chance, name="new_chance"),
    path("edit_chance/<int:chance_id>/", views.edit_chance, name="edit_chance"),
    path("delete_chance/<int:chance_id>/", views.delete_chance, name="delete_chance"),
    path("collab/", views.collab, name="collab"),
    path(
        "collab_refer_detail/<int:refer_id>/",
        views.collab_refer_detail,
        name="collab_refer_detail",
    ),
    path("collab_report/<int:refer_id>/", views.collab_report, name="collab_report"),
    path(
        "collab_report_one/<int:refer_id>/",
        views.collab_report_one,
        name="collab_report_one",
    ),
    path("crm_refers/", views.crm_refers, name="crm_refers"),
    path("collab_kanban/", views.collab_kanban, name="collab_kanban"),
    path(
        "partial_collab_kanban/",
        views.partial_collab_kanban,
        name="partial_collab_kanban",
    ),
    path(
        "collab_schedule/<int:refer_id>/", views.collab_schedule, name="collab_schedule"
    ),
    path(
        "collab_schedule_one/<int:refer_id>/",
        views.collab_schedule_one,
        name="collab_schedule_one",
    ),
    path(
        "collab_refer_archive/<int:refer_id>/",
        views.collab_refer_archive,
        name="collab_refer_archive",
    ),
    path(
        "collab_refer_file_upload/<int:refer_id>/",
        views.collab_refer_file_upload,
        name="collab_refer_file_upload",
    ),
    path(
        "collab_refer_file_delete/<int:file_id>/",
        views.collab_refer_file_delete,
        name="collab_refer_file_delete",
    ),
    path(
        "collab_refer_file_delete_all/<int:refer_id>/",
        views.collab_refer_file_delete_all,
        name="collab_refer_file_delete_all",
    ),
    path(
        "collab_refer_files/<int:refer_id>/",
        views.collab_refer_files,
        name="collab_refer_files",
    ),
    path("dicom_viewer/<int:refer_id>/", views.dicom_viewer, name="dicom_viewer"),
]
