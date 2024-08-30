from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    # path("profile/edit/", views.profile_edit, name="profile_edit"),
    # path("profile/delete/", views.profile_delete, name="profile_delete"),
]
