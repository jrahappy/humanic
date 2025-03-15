from django.urls import path
from . import views

app_name = "web"
urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("clinicContact/", views.clinicContact, name="clinicContact"),
    path("doctorContact/", views.doctorContact, name="doctorContact"),
]
