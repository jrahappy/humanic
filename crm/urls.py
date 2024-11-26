from django.urls import path
from . import views

app_name = "crm"
urlpatterns = [
    path("", views.index, name="index"),
    path("new_opp/<int:company_id>/", views.new_opp, name="new_opp"),
    path("opps_customer/<int:company_id>/", views.opps_customer, name="opps_customer"),
    path("edit_opp/<int:opp_id>/", views.edit_opp, name="edit_opp"),
    path("delete_opp/<int:opp_id>/", views.delete_opp, name="delete_opp"),
    path("chances/", views.chances, name="chances"),
    path("new_chance/", views.new_chance, name="new_chance"),
    path("edit_chance/<int:chance_id>/", views.edit_chance, name="edit_chance"),
    path("delete_chance/<int:chance_id>/", views.delete_chance, name="delete_chance"),
]
