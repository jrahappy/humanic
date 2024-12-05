from django.urls import path
from . import views

app_name = "collab"
urlpatterns = [
    path("", views.index, name="index"),
    path("refer_list/<int:company_id>/", views.refer_list, name="refer_list"),
    path("refer_create/", views.refer_create, name="refer_create"),
    path("refer_detail/<int:refer_id>/", views.refer_detail, name="refer_detail"),
    path("refer_update/<int:refer_id>/", views.refer_update, name="refer_update"),
    path("company_info/<int:company_id>/", views.company_info, name="company_info"),
    path(
        "company_update/<int:company_id>/", views.company_update, name="company_update"
    ),
    path("profile/", views.profile, name="profile"),
]
