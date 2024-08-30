from django.urls import path

from . import views

app_name = "briefing"
urlpatterns = [
    path("", views.index, name="index"),
]
