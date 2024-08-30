from django.urls import path

from .views import index, platform

app_name = "product"

urlpatterns = [
    path("", index, name="index"),
    path("platform/", platform, name="platform"),
]
