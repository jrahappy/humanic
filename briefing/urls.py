from django.urls import path

from . import views

app_name = "briefing"
urlpatterns = [
    path("", views.index, name="index"),
    path("partial_briefing", views.partial_briefing, name="partial_briefing"),
]
