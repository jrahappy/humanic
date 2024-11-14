from django.urls import path
from . import views

app_name = "referdex"
urlpatterns = [
    path("", views.index, name="index"),
]
