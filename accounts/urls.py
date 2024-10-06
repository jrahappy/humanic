from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("user_update", views.user_update, name="user-update"),
    path(
        "change_password/",
        views.CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    # path("profile/edit/", views.profile_edit, name="profile_edit"),
    # path("profile/delete/", views.profile_delete, name="profile_delete"),
]
