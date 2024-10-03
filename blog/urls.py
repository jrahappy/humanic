from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_post, name="create"),
    path("detail/<int:pk>/", views.detail, name="detail"),
    path("update/<int:pk>/", views.update_post, name="update"),
    path("delete/<int:pk>/", views.delete_post, name="delete"),
]
