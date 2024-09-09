from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "importdata"
urlpatterns = [
    path("", views.index, name="index"),
    path("history_delete/<int:id>/", views.history_delete, name="history_delete"),
    path("new_upload", views.new_upload, name="new_upload"),
    path("create_rawdata/<int:id>/", views.create_rawdata, name="create_rawdata"),
    path("initial_dr_data/", views.initial_dr_data, name="initial_dr_data"),
    path("temp_doctor/", views.temp_doctor, name="temp_doctor"),
    path(
        "initial_customer_data/",
        views.initial_customer_data,
        name="initial_customer_data",
    ),
    path(
        "temp_customer_import/", views.temp_customer_import, name="temp_customer_import"
    ),
    path("temp_customer/", views.temp_customer, name="temp_customer"),
    # path("temp_customer_view/", views.temp_customer_view, name="temp_customer_view"),
    # path("temp_customer_clean/", views.temp_customer_clean, name="temp_customer_clean"),
    # path("preview", views.preview, name="preview"),
    # path("rawdata", views.rawdata, name="rawdata"),
    # path("upload/", views.upload, name="upload"),
    # path("delete/<int:id>/", views.delete, name="delete"),
    # path("edit/<int:id>/", views.edit, name="edit"),
    # path("update/<int:id>/", views.update, name="update"),
    # path("export/", views.export, name="export"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
