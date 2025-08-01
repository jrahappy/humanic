from django.urls import path
from . import views

app_name = "collab"
urlpatterns = [
    path("test/", views.test, name="test"),
    path("", views.index, name="index"),
    path("clean_refer/", views.clean_refer, name="clean_refer"),
    path("home/", views.home, name="home"),
    path("stat/", views.stat, name="stat"),
    path("stat_tele/", views.stat_tele, name="stat_tele"),
    path("partial_stat_tele", views.partial_stat_tele, name="partial_stat_tele"),
    path(
        "partial_stat_filtered/<int:company_id>/",
        views.partial_stat_filtered,
        name="partial_stat_filtered",
    ),
    path("refer_list/<int:company_id>/", views.refer_list, name="refer_list"),
    path("refer_create/", views.refer_create, name="refer_create"),
    path("refer_detail/<int:refer_id>/", views.refer_detail, name="refer_detail"),
    path("refer_print/<int:refer_id>/", views.refer_print, name="refer_print"),
    path(
        "return_report_print/<int:refer_id>/",
        views.return_report_print,
        name="return_report_print",
    ),
    path("refer_update/<int:refer_id>/", views.refer_update, name="refer_update"),
    path("refer_delete/<int:refer_id>/", views.refer_delete, name="refer_delete"),
    path(
        "refer_completed/<int:refer_id>/", views.refer_completed, name="refer_completed"
    ),
    path("refer_archive/<int:refer_id>/", views.refer_archive, name="refer_archive"),
    path("company_info/<int:company_id>/", views.company_info, name="company_info"),
    path(
        "company_update/<int:company_id>/", views.company_update, name="company_update"
    ),
    path("profile/", views.profile, name="profile"),
    path("illness_list/", views.illness_list, name="illness_list"),
    path("illness_code_import/", views.illness_code_import, name="illness_code_import"),
    path("simplecode_list/", views.simplecode_list, name="simplecode_list"),
    path("simplecode_import/", views.simplecode_import, name="simplecode_import"),
    path(
        "partial_simple_list/<int:refer_id>/",
        views.partial_simple_list,
        name="partial_simple_list",
    ),
    path(
        "partial_simple_diagnosis_list/<int:refer_id>/",
        views.partial_simple_diagnosis_list,
        name="partial_simple_diagnosis_list",
    ),
    path(
        "delete_simple_diagnosis/<int:simple_id>/",
        views.delete_simple_diagnosis,
        name="delete_simple_diagnosis",
    ),
    path(
        "create_simple_diagnosis/<int:refer_id>/<int:simple_id>/",
        views.create_simple_diagnosis,
        name="create_simple_diagnosis",
    ),
    path(
        "partial_illness_code_list/<int:refer_id>/",
        views.partial_illness_code_list,
        name="partial_illness_code_list",
    ),
    path(
        "partial_illness_code_search/<int:refer_id>/",
        views.partial_illness_code_search,
        name="partial_illness_code_search",
    ),
    path(
        "partial_illness_list/<int:refer_id>/",
        views.partial_illness_list,
        name="partial_illness_list",
    ),
    path(
        "create_refer_illness/<int:refer_id>/<int:illness_id>/",
        views.create_refer_illness,
        name="create_refer_illness",
    ),
    path(
        "delete_refer_illness/<int:refer_illness_id>/",
        views.delete_refer_illness,
        name="delete_refer_illness",
    ),
    path(
        "partial_my_illness_code_list<int:refer_id>/",
        views.partial_my_illness_code_list,
        name="partial_my_illness_code_list",
    ),
    path(
        "add_my_illness_code/<int:refer_id>/<int:illness_id>/",
        views.add_my_illness_code,
        name="add_my_illness_code",
    ),
    path(
        "delete_my_illness_code/<int:refer_id>/<int:illness_id>/",
        views.delete_my_illness_code,
        name="delete_my_illness_code",
    ),
    path(
        "partial_my_simple_diagonosis_list/<int:refer_id>/",
        views.partial_my_simple_diagonosis_list,
        name="partial_my_simple_diagonosis_list",
    ),
    path(
        "add_my_simple_code/<int:refer_id>/<int:simple_id>/",
        views.add_my_simple_code,
        name="add_my_simple_code",
    ),
    path(
        "delete_my_simple_code/<int:simple_id>/",
        views.delete_my_simple_code,
        name="delete_my_simple_code",
    ),
    path(
        "password/change/",
        views.password_change,
        name="change_password",
    ),
    path(
        "password/change/done/", views.password_change_done, name="password_change_done"
    ),
    path("working_setting/", views.working_setting, name="working_setting"),
    path("workhour_create/<int:id>/", views.workhour_create, name="workhour_create"),
    path("workhour_remove/<int:id>/", views.workhour_remove, name="workhour_remove"),
    path("holiday_create/", views.holiday_create, name="holiday_create"),
    path("holiday_remove/", views.holiday_remove, name="holiday_remove"),
    path(
        "make_csv_tele/<int:company_id>/<str:date>/",
        views.make_csv_tele,
        name="make_csv_tele",
    ),
]
