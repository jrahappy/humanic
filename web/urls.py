from django.urls import path
from . import views

app_name = "web"
urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("clinicContact/", views.clinicContact, name="clinicContact"),
    path(
        "clinicContact_success/",
        views.clinicContact_success,
        name="clinicContact_success",
    ),
    path("doctorContact/", views.doctorContact, name="doctorContact"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("email_policy/", views.email_policy, name="email_policy"),
    path("specialties/", views.specialties, name="specialties"),
    path("intro/", views.intro, name="intro"),
    path("faq/", views.faq, name="faq"),
]
