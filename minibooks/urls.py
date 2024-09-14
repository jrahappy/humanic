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
    path("clean_data/<int:id>/", views.clean_data, name="clean_data"),
    # path("unverified_data/<int:id>/", views.unverified_data, name="unverified_data"),
    # path("update_cleandata/<int:id>/", views.update_cleandata, name="update_cleandata"),
    # path("initial_dr_data/", views.initial_dr_data, name="initial_dr_data"),
    # path("temp_doctor/", views.temp_doctor, name="temp_doctor"),
    # path(
    #     "initial_customer_data/",
    #     views.initial_customer_data,
    #     name="initial_customer_data",
    # ),
    # path(
    #     "temp_customer_import/", views.temp_customer_import, name="temp_customer_import"
    # ),
    # path("temp_customer/", views.temp_customer, name="temp_customer"),
]
