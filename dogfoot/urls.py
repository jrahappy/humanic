from django.urls import path
from . import views

app_name = "dogfoot"
urlpatterns = [
    path("", views.home, name="home"),
    path("everything/", views.schema, name="everything"),
    path("table/<str:app_name>", views.get_tables, name="get-tables"),
    path(
        "table/<str:app_name>/<str:model_name>/generate",
        views.dj_code_generate,
        name="dj-code-generate",
    ),
    path("choices", views.choice_list, name="choice-list"),
    path("choices/create", views.choice_create, name="choice-create"),
    path("choices/<int:pk>/delete", views.choice_delete, name="choice-delete"),
    path("choices/<int:pk>/update", views.choice_update, name="choice-update"),
    path("show-urls/", views.show_urls, name="show-urls"),
    path("show-funcs/", views.show_funcs, name="show-funcs"),
    path("update_icaseimage_table/", views.extension_update, name="ext-update"),
    path(
        "update_clinic_user_table/",
        views.patient_clinic_update,
        name="patient-clinic-update",
    ),
    # path("megamenu/create", views.mega_menu_create, name="mega-menu-create"),
    # path("megamenu/<int:pk>/delete", views.mega_menu_delete, name="mega-menu-delete"),
    # path("megamenu/<int:pk>/update", views.mega_menu_update, name="mega-menu-update"),
]
