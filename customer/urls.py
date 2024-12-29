from django.urls import path

from . import views

app_name = "customer"
urlpatterns = [
    path("", views.index, name="index"),
    path("search_company/", views.search_company, name="search_company"),
    path("new_customer/", views.new_customer, name="new_customer"),
    path("new/", views.new, name="new"),
    path("detail/<int:customer_id>/", views.detail, name="detail"),
    path(
        "add_collab_login_user/<int:customer_id>/",
        views.add_collab_login_user,
        name="add_collab_login_user",
    ),
    path("edit_customer/<int:customer_id>/", views.edit_customer, name="edit_customer"),
    path("contracts/<int:company_id>/", views.contracts, name="contracts"),
    path(
        "delete_contract/<int:company_id>/<int:contract_id>/",
        views.delete_contract,
        name="delete_contract",
    ),
    path(
        "detail/<int:company_id>/new_contract/",
        views.new_contract,
        name="new_contract",
    ),
    path(
        "detail/<int:company_id>/new_contract_detail/<int:contract_id>/",
        views.new_contract_detail,
        name="new_contract_detail",
    ),
    path(
        "update/<int:customer_id>/",
        views.update,
        name="update",
    ),
    path("clogs/<int:company_id>/", views.clogs, name="clogs"),
    path("new_clog/<int:company_id>/", views.new_clog, name="new_clog"),
    path(
        "delete_clog/<int:company_id>/<int:clog_id>/",
        views.delete_clog,
        name="delete_clog",
    ),
    path("contacts/<int:company_id>/", views.contacts, name="contacts"),
    path("new_contact/<int:company_id>/", views.new_contact, name="new_contact"),
    path(
        "delete_contact/<int:company_id>/<int:contact_id>/",
        views.delete_contact,
        name="delete_contact",
    ),
    path(
        "edit_contact/<int:company_id>/<int:contact_id>/",
        views.edit_contact,
        name="edit_contact",
    ),
    path("cfiles/<int:company_id>/", views.cfiles, name="cfiles"),
    path("cfile_upload/<int:company_id>/", views.cfile_upload, name="cfile_upload"),
    path(
        "cfile_delete/<int:company_id>/<int:cfile_id>/",
        views.cfile_delete,
        name="cfile_delete",
    ),
    path(
        "tag_delete/<int:company_id>/<int:tag_id>/",
        views.tag_delete,
        name="tag_delete",
    ),
]
