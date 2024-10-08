from django.urls import path

from . import views

app_name = "customer"
urlpatterns = [
    path("", views.index, name="index"),
    path("search_company/", views.search_company, name="search_company"),
    path("new_customer/", views.new_customer, name="new_customer"),
    path("new/", views.new, name="new"),
    path("detail/<int:customer_id>/", views.detail, name="detail"),
    path("edit_customer/<int:customer_id>/", views.edit_customer, name="edit_customer"),
    path(
        "detail/<int:customer_id>/new_contract/",
        views.new_contract,
        name="new_contract",
    ),
    path(
        "detail/<int:customer_id>/new_contract_detail/<int:contract_id>/",
        views.new_contract_detail,
        name="new_contract_detail",
    ),
    path(
        "update/<int:customer_id>/",
        views.update,
        name="update",
    ),
    # path("edit/<int:customer_id>/", views.edit_customer, name="edit_customer"),
    # path("delete/<int:customer_id>/", views.delete_customer, name="delete_customer"),
]
