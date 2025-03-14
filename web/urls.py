from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("customer/", views.customer, name="customer"),
    path("provider/", views.provider, name="provider"),
]
