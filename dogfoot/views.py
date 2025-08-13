from django.shortcuts import render
from django.apps import apps
from django.db import connection
from django.forms import modelformset_factory
from .models import MegaChoices, MegaChoiceNames
from .utils import (
    get_dj_code_generate,
    get_table_app,
    get_all_url_patterns,
)

# from icases.models import ICaseImage, ICase
from django.urls import get_resolver
import json
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser as User


@login_required
def diagrams(request):

    context = {"apps": {}}

    app_configs = apps.get_app_configs()

    for app_config in app_configs:
        app_name = app_config.name
        if (
            "django" in app_name
            or "allauth" in app_name
            or "crispy" in app_name
            or "debug" in app_name
            or "social" in app_name
            or "server" in app_name
            or "storages" in app_name
            or "widget_tweaks" in app_name
            or "tailwind" in app_name
            or "theme" in app_name
            or "import_export" in app_name
            or "ckeditor" in app_name
            or "celery_progress" in app_name
        ):
            pass
        else:
            context["apps"][app_name] = {"models": {}}

            got_models = app_config.get_models()
            for model in got_models:
                model_name = model.__name__
                context["apps"][app_name]["models"][model_name] = {"fields": {}}

                fields = model._meta.get_fields()
                for field in fields:
                    field_name = field.name
                    field_type = field.get_internal_type()
                    related_table = getattr(field, "related_model", None)
                    related_table_name = (
                        related_table._meta.db_table if related_table else "N/A"
                    )
                    field_attributes = {
                        "type": field_type,
                        "related_table": related_table_name,
                        # "verbose_name": field.verbose_name,
                        # "blank": field.blank,
                        "choices": getattr(field, "choices", "N/A"),
                        # "default": field.default if callable(field.default) else str(field.default),
                        # "help_text": field.help_text,
                        "max_length": getattr(field, "max_length", "N/A"),
                        # "null": field.null,
                        "unique": getattr(field, "unique", "N/A"),
                    }
                    context["apps"][app_name]["models"][model_name]["fields"][
                        field_name
                    ] = field_attributes

        # print(context)
    return render(request, "dogfoot/diagrams.html", context)


# 이 함수는  Staff이 환자 정보를 추가한 경우에 병원 정보가 누락된 환자들에 대해 병원 정보를 추가하는 함수입니다.
@login_required
def patient_clinic_update(request):
    patients = User.objects.filter(is_consumer=True, clinic=0)
    i = 0
    for patient in patients:
        icase = ICase.objects.filter(user=patient).first()
        if icase:
            patient.clinic = icase.referred_by.id
            patient.save()
            i += 1

    return render(request, "dogfoot/patient_clinic_update.html", {"i": i})


def extension_update(request):
    icase_images = ICaseImage.objects.all()
    i = 0
    for icase_image in icase_images:
        icase_image.file_extension = (
            icase_image.afile.name.split(".")[-1].lower().strip()
        )
        icase_image.save()
        i += 1
    return render(request, "dogfoot/extension_update.html" % i)


def show_funcs(request):
    context = {"app_names": app_names()}
    return render(request, "dogfoot/show_funcs.html", context)


def app_names():
    app_configs = apps.get_app_configs()
    app_names = [
        app_config.name
        for app_config in app_configs
        if "django" not in app_config.name
        if "allauth" not in app_config.name
        if "crispy" not in app_config.name
        if "debug" not in app_config.name
        if "server" not in app_config.name
        if "ckeditor" not in app_config.name
        if "celery_progress" not in app_config.name
    ]
    return app_names


def home(request):
    context = {"app_names": app_names()}

    return render(request, "dogfoot/home.html", context)


def show_urls(request, app_name=None):
    app_names = get_app_names

    app_name = request.GET.get("app_name", "")
    if app_name is not None and "all" not in app_name:
        urlpatterns = get_all_url_patterns(
            get_resolver(None).url_patterns, app_filter=app_name
        )
    else:
        urlpatterns = get_all_url_patterns(get_resolver(None).url_patterns)

    urlpatterns_json = json.dumps(urlpatterns)

    context = {
        "app_name": app_name,
        "app_names": app_names,
        "urlpatterns": urlpatterns_json,
    }

    return render(request, "dogfoot/show_urls.html", context)


def choice_list(request):
    choices = MegaChoiceNames.objects.all().order_by("name", "order")
    context = {
        "choices": choices,
    }
    return render(request, "dogfoot/choice_list.html", context)


def choice_create(request):

    MegaChoicesFormSet = modelformset_factory(MegaChoices, fields="__all__", extra=1)
    if request.method == "POST":
        formset = MegaChoicesFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return render(request, "dogfoot/choice_list.html")
    else:
        formset = MegaChoicesFormSet()
        return render(request, "dogfoot/choice_create.html", {"formset": formset})


def choice_delete(request, pk):
    return render(request, "dogfoot/choice_delete.html")


def choice_update(request, pk):
    return render(request, "dogfoot/choice_update.html")


def schema(request):
    context = {"apps": {}}

    app_configs = apps.get_app_configs()

    for app_config in app_configs:
        app_name = app_config.name
        if (
            "django" in app_name
            or "allauth" in app_name
            or "crispy" in app_name
            or "debug" in app_name
            or "social" in app_name
            or "server" in app_name
            or "storages" in app_name
            or "widget_tweaks" in app_name
            or "tailwind" in app_name
            or "theme" in app_name
            or "import_export" in app_name
            or "ckeditor" in app_name
            or "celery_progress" in app_name
        ):
            pass
        else:
            context["apps"][app_name] = {"models": {}}

            got_models = app_config.get_models()
            for model in got_models:
                model_name = model.__name__
                context["apps"][app_name]["models"][model_name] = {"fields": {}}

                fields = model._meta.get_fields()
                for field in fields:
                    field_name = field.name
                    field_type = field.get_internal_type()
                    related_table = getattr(field, "related_model", None)
                    related_table_name = (
                        related_table._meta.db_table if related_table else "N/A"
                    )
                    field_attributes = {
                        "type": field_type,
                        "related_table": related_table_name,
                        # "verbose_name": field.verbose_name,
                        # "blank": field.blank,
                        "choices": getattr(field, "choices", "N/A"),
                        # "default": field.default if callable(field.default) else str(field.default),
                        # "help_text": field.help_text,
                        "max_length": getattr(field, "max_length", "N/A"),
                        # "null": field.null,
                        "unique": getattr(field, "unique", "N/A"),
                    }
                    context["apps"][app_name]["models"][model_name]["fields"][
                        field_name
                    ] = field_attributes

        # print(context)

    return render(request, "dogfoot/schema.html", context)


app_name = []


def get_app_names():
    app_configs = apps.get_app_configs()
    app_names = [
        app_config.name
        for app_config in app_configs
        if "django" not in app_config.name
        if "allauth" not in app_config.name
        if "crispy" not in app_config.name
        if "debug" not in app_config.name
        if "server" not in app_config.name
        if "widget_tweaks" not in app_config.name
        if "tailwind" not in app_config.name
        if "theme" not in app_config.name
        if "import_export" not in app_config.name
        if "dogfoot" not in app_config.name
        if "utils" not in app_config.name
    ]
    return app_names


def all_tables(request):
    app_configs = apps.get_app_configs()
    app_names = get_app_names

    with connection.cursor() as cursor:
        all_table_names = connection.introspection.table_names()
        app_table_names = [name for name in all_table_names]
        table_columns = {
            table: connection.introspection.get_table_description(cursor, table)
            for table in app_table_names
        }

    return render(
        request,
        "dogfoot/table.html",
        {
            "table_columns": table_columns,
            "app_name": app_name,
            "app_names": app_names,
        },
    )


def get_tables(request, app_name):

    app_configs = apps.get_app_configs()
    app_names = get_app_names

    if app_name == "all":

        with connection.cursor() as cursor:
            all_table_names = connection.introspection.table_names()
            app_table_names = [name for name in all_table_names]
            table_columns = {
                table: connection.introspection.get_table_description(cursor, table)
                for table in app_table_names
            }

        return render(
            request,
            "dogfoot/table.html",
            {
                "table_columns": table_columns,
                "app_name": app_name,
                "app_names": app_names,
            },
        )
    else:

        with connection.cursor() as cursor:
            all_table_names = connection.introspection.table_names()
            app_table_names = [
                name for name in all_table_names if name.startswith(app_name + "_")
            ]
            table_columns = {
                table: connection.introspection.get_table_description(cursor, table)
                for table in app_table_names
            }
            # print("table_columns: ", table_columns)
        return render(
            request,
            "dogfoot/table.html",
            {
                "table_columns": table_columns,
                "app_name": app_name,
                "app_names": app_names,
            },
        )


def dj_code_generate(request, app_name, model_name):

    app_configs = apps.get_app_configs()
    app_names = get_app_names
    code_gen = get_dj_code_generate(app_name, model_name)
    table_columns = get_table_app(request, app_name)

    return render(
        request,
        "dogfoot/dj_code_generate.html",
        {
            "code_gen": code_gen,
            "table_columns": table_columns,
            "app_name": app_name,
            "model_name": model_name,
            "app_names": app_names,
        },
    )
