from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("user_update", views.user_update, name="user-update"),
    path("password_change/", views.password_change, name="password_change"),
    path(
        "password_change/done/", views.password_change_done, name="password_change_done"
    ),
    # path(
    #     "change_password/",
    #     views.CustomPasswordChangeView.as_view(),
    #     name="change_password",
    # ),
    # path("signup/", views.signup, name="account_signup"),
    # path("profile/edit/", views.profile_edit, name="profile_edit"),
    # path("profile/delete/", views.profile_delete, name="profile_delete"),
]
