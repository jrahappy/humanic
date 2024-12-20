from django.urls import path
from . import views

app_name = "collab"
urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("refer_list/<int:company_id>/", views.refer_list, name="refer_list"),
    path("refer_create/", views.refer_create, name="refer_create"),
    path("refer_detail/<int:refer_id>/", views.refer_detail, name="refer_detail"),
    path("refer_update/<int:refer_id>/", views.refer_update, name="refer_update"),
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
        "/partial_simple_list/<int:refer_id>/",
        views.partial_simple_list,
        name="partial_simple_list",
    ),
    path(
        "/partial_simple_diagnosis_list/<int:refer_id>/",
        views.partial_simple_diagnosis_list,
        name="partial_simple_diagnosis_list",
    ),
    path(
        "/delete_simple_diagnosis/<int:simple_id>/",
        views.delete_simple_diagnosis,
        name="delete_simple_diagnosis",
    ),
    path(
        "/create_simple_diagnosis/<int:refer_id>/<int:simple_id>/",
        views.create_simple_diagnosis,
        name="create_simple_diagnosis",
    ),
    path(
        "/partial_illness_code_list/<int:refer_id>/",
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
]
