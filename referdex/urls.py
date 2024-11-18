from django.urls import path
from . import views

app_name = "referdex"
urlpatterns = [
    path("", views.index, name="index"),
    path("pm", views.pm, name="pm"),
    path("partial_pm", views.partial_pm, name="partial_pm"),
    path("pm_create/", views.pm_create, name="pm_create"),
    path("pm_edit/<int:pm_id>/", views.pm_edit, name="pm_edit"),
    path("pm_delete/<int:pm_id>/", views.pm_delete, name="pm_delete"),
    path("pm_detail/<int:pm_id>/", views.pm_detail, name="pm_detail"),
    path(
        "pmd_list_by_provider/<int:pm_id>/<int:provider_id>/",
        views.pmd_list_by_provider,
        name="pmd_list_by_provider",
    ),
    path(
        "pm_assign/<int:pm_id>/<int:provider_id>/<str:modality>/",
        views.pm_assign,
        name="pm_assign",
    ),
    path("pmds/<int:pm_id>/", views.pmds, name="pmds"),
    path("pmd_delete/<int:pmd_id>/", views.pmd_delete, name="pmd_delete"),
    path(
        "match_rule_create/<int:provider_id>/",
        views.match_rule_create,
        name="match_rule_create",
    ),
    path(
        "partial_match_rules/<int:provider_id>/",
        views.partial_match_rules,
        name="partial_match_rules",
    ),
    path(
        "match_rule_delete/<int:match_rule_id>/",
        views.match_rule_delete,
        name="match_rule_delete",
    ),
    path(
        "match_rule_detail/<int:match_rule_id>/",
        views.match_rule_detail,
        name="match_rule_detail",
    ),
]
