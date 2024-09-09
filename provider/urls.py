from django.urls import path

from . import views

app_name = "provider"

urlpatterns = [
    path("", views.index, name="index"),
    path("rawdata", views.rawdata, name="rawdata"),
    path("create_user_rawdata", views.create_user_rawdata, name="create_user_rawdata"),
    path("update_profile", views.update_profile, name="update_profile"),
]
