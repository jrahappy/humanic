from django.urls import path

from . import views

app_name = "provider"

urlpatterns = [
    path("", views.index, name="index"),
    path("new_provider", views.new_provider, name="new_provider"),
    path("view_provider/<int:id>/", views.view_provider, name="view_provider"),
    path("edit_provider/<int:id>/", views.edit_provider, name="edit_provider"),
    path("edit/<int:id>/", views.edit, name="edit"),
    path("hr_file_upload/<int:id>/", views.hr_file_upload, name="hr_file_upload"),
    path("hr_files/<int:id>/", views.partial_hr_files, name="hr_files"),
    path(
        "delete_hr_file/<int:provider_id>/<int:file_id>/",
        views.delete_hr_file,
        name="delete_hr_file",
    ),
    # path("rawdata", views.rawdata, name="rawdata"),
    # path("create_user_rawdata", views.create_user_rawdata, name="create_user_rawdata"),
    # path("update_profile", views.update_profile, name="update_profile"),
]
