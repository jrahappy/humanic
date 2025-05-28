from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet

app_name = "api"
rounder = DefaultRouter()
rounder.register(r"companies", CompanyViewSet, basename="company")
urlpatterns = [
    path("", include(rounder.urls)),
]
