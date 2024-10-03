from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("partial_dashboard", views.partial_dashboard, name="partial_dashboard"),
    path("daisyui/", views.daisyui, name="daisyui"),
]
