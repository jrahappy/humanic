from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path("", views.home, name="home"),
    path("index/", views.index, name="index"),
    path("create_admin/", views.create_post_admin, name="create_admin"),
    path("detail/<int:pk>/", views.detail, name="detail"),
    path("create/", views.create_post, name="create"),
    path("update/<int:pk>/", views.update_post, name="update"),
    path("delete/<int:pk>/", views.delete_post, name="delete"),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
]
