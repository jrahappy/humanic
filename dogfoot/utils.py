from django.db import connection
from .models import MegaChoices, MegaMenuSub
from django.urls import URLPattern, URLResolver
from collections import defaultdict
from inspect import signature, Parameter
import secrets
import string


def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    return password


def get_menu(menu_id, clinic_id=None, sm_id=None):

    mega_menu_sub = (
        MegaMenuSub.objects.filter(name__id=menu_id, is_active=True)
        .select_related("name")
        .order_by("ordery", "orderx")
    )

    if sm_id is not None:
        sm_id = str(sm_id)
    else:
        sm_id = "0"

    menu_html = '<div class="d-flex flex-column flex-shrink-0 p-3 bg-body-light vh-100 border-end" style="width: 280px;">'
    menu_html += '<ul class="nav nav-pills flex-column mb-auto">'

    flag = True
    for sub in mega_menu_sub:
        url = sub.url
        if url is not None:
            url = f"{url}?sm_id={sub.id}"
        else:
            url = "#"

        if sub.orderx == 0:
            if flag == False:
                menu_html += "</ul>"
                flag = True
            if sub.id == int(sm_id):
                menu_html += f'<li class="nav-item" id={sub.id}">'
                menu_html += (
                    f'<a href="{url}" class="nav-link active" aria-current="page">'
                )
                menu_html += f"{sub.css_class}&nbsp;&nbsp;"
                menu_html += f"{sub.sub_name}</a></li>"
            else:
                menu_html += f'<li class="nav-item" id="{sub.id}">'
                menu_html += f'<a href="{url}" class="nav-link link-body-emphasis ms-2" aria-current="page">'
                menu_html += f"{sub.css_class}&nbsp;&nbsp;"
                menu_html += f"{sub.sub_name}</a></li>"
        else:
            if flag == True:
                menu_html += '<ul class="nav nav-pills ms-4 flex-column mb-auto">'
                flag = False

            if sub.id == int(sm_id):
                menu_html += f'<li class="nav-item ps-2" id="{sub.id}">'
                menu_html += (
                    f'<a href="{url}" class="nav-link active" aria-current="page">'
                )
                menu_html += f"{sub.sub_name}</a></li>"
            else:
                menu_html += f'<li class="nav-item ps-2" id="{sub.id}">'
                menu_html += f'<a href="{url}" class="nav-link link-body-emphasis">'
                menu_html += f"{sub.sub_name}</a></li>"

    if flag == False:
        menu_html += "</ul>"

    menu_html += "</ul></div>"

    return menu_html


def get_all_url_patterns(urlpatterns, prefix="", app_filter=None):
    url_patterns = defaultdict(list)
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            new_prefix = prefix + str(pattern.pattern)
            deeper_patterns = get_all_url_patterns(
                pattern.url_patterns, new_prefix, app_filter
            )
            for app, patterns in deeper_patterns.items():
                url_patterns[app].extend(patterns)
        elif isinstance(pattern, URLPattern):
            app_name = pattern.callback.__module__.split(".")[0]
            if app_filter is None or app_name == app_filter:
                sig = signature(pattern.callback)
                arg_types = {
                    name: str(param.annotation)
                    for name, param in sig.parameters.items()
                    if param.kind == Parameter.POSITIONAL_OR_KEYWORD
                }
                url_patterns[app_name].append(
                    (
                        prefix + str(pattern.pattern),
                        pattern.callback.__name__,
                        pattern.name,
                        arg_types,
                    )
                )
    return url_patterns


# def get_all_url_patterns(urlpatterns, prefix="", app_name="no_app"):
#     url_patterns = defaultdict(list)
#     for pattern in urlpatterns:
#         if isinstance(pattern, URLResolver):
#             # If this is an included URLconf, explore this one recursively
#             new_prefix = prefix + str(pattern.pattern)
#             new_app_name = pattern.app_name if pattern.app_name else app_name
#             deeper_patterns = get_all_url_patterns(
#                 pattern.url_patterns, new_prefix, new_app_name
#             )
#             for app, patterns in deeper_patterns.items():
#                 url_patterns[app].extend(patterns)
#         elif isinstance(pattern, URLPattern):
#             # Add the URL pattern (prefix + actual pattern), its corresponding view function, and app name
#             url_patterns[app_name].append(
#                 (prefix + str(pattern.pattern), pattern.callback)
#             )
#     return url_patterns


def get_choices(request, choice_name, selected_key, html_type, css_class):
    choices = MegaChoices.objects.get(name=choice_name)
    html_text = ""
    temp_choices = [
        (getattr(choices, "c" + str(i)), getattr(choices, "c" + str(i)))
        for i in range(3)
    ]

    if html_type == "select":
        html_text += f'<select name="{choice_name}" class="{css_class}">'
        for choice in temp_choices:
            if choice[0] == selected_key:
                html_text += (
                    f'<option value="{choice[0]}" selected>{choice[1]}</option>'
                )
            else:
                html_text += f'<option value="{choice[0]}">{choice[1]}</option>'

    elif html_type == "radio":
        for choice in temp_choices:
            if choice[0] == selected_key:
                html_text += f'<input type="radio" class="{css_class}" name="{choice_name}" value="{choice[0]}" checked>{choice[1]}<br>'
            else:
                html_text += f'<input type="radio" class="{css_class}" name="{choice_name}" value="{choice[0]}">{choice[1]}<br>'

    elif html_type == "checkbox":
        for choice in temp_choices:
            if choice[0] == selected_key:
                html_text += f'<input type="checkbox" class="{css_class}" name="{choice_name}" value="{choice[0]}" checked>{choice[1]}<br>'
            else:
                html_text += f'<input type="checkbox" class="{css_class}" name="{choice_name}" value="{choice[0]}">{choice[1]}<br>'
    elif html_type == "button":
        for choice in temp_choices:
            html_text += f'<button type="button" class="{css_class}" name="{choice_name}" value="{choice[0]}">{choice[1]}</button>'

    elif html_type == "link":
        for choice in temp_choices:
            html_text += f'<a href="{choice[0]}" class="{css_class}" name="{choice_name}" value="{choice[0]}">{choice[1]}</a>'
    elif html_type == "list":
        html_text = f'<ul class="{css_class}">'
        for choice in temp_choices:
            html_text += f"<li>{choice[1]}</li>"
        html_text += "</ul>"
    elif html_type == "table":
        html_text = f'<table class="{css_class}">'
        for choice in temp_choices:
            html_text += f"<tr><td>{choice[1]}</td></tr>"
        html_text += "</table>"
    elif html_type == "div":
        html_text = f'<div class="{css_class}">'
        for choice in temp_choices:
            html_text += f"<div>{choice[1]}</div>"
        html_text += "</div>"
    elif html_type == "inputbox":
        html_text = f'<input type="text" class="{css_class}" name="{choice_name}" value="{selected_key}" class="{css_class or "form-control"}">'
    elif html_type == "only+text":
        for choice in temp_choices:
            if choice[0] == selected_key:
                html_text = f"{choice[1]}"
    else:
        html_text = "Not found."

    choices = html_text
    return choices


def get_table_app(request, app_name):
    with connection.cursor() as cursor:
        all_table_names = connection.introspection.table_names()
        app_table_names = [
            name for name in all_table_names if name.startswith(app_name + "_")
        ]
        table_columns = {
            table: connection.introspection.get_table_description(cursor, table)
            for table in app_table_names
        }
        # print("table_columns: ", table_columns.values())
        return table_columns


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


def get_dj_code_generate(app_name, model_name):

    prefix = app_name.__len__() + 1
    model_name = model_name[prefix:]

    # for urls.py
    urls_gen = ""
    urls_gen += f"\npath('{model_name}/', include('{app_name}.urls'))"
    urls_gen += (
        f"\npath('{model_name}/', views.{model_name}_list, name='{model_name}-list')"
    )
    urls_gen += f"\npath('{model_name}/create/', views.{model_name}_create, name='{model_name}-create')"
    urls_gen += f"\npath('{model_name}/<int:pk>', views.{model_name}_detail, name='{model_name}-detail')"
    urls_gen += f"\npath('{model_name}/<int:pk>/update', views.{model_name}_update, name='{model_name}-edit')"
    urls_gen += f"\npath('{model_name}/<int:pk>/delete', views.{model_name}_delete, name='{model_name}-delete')"
    urls_gen = html_escape(urls_gen).strip()

    # # for views.py
    views_gen = f"def {model_name}_list(request):"
    views_gen += f"\n    {model_name}s = {model_name}.objects.all()"
    views_gen += f"\n    return render(request, '{app_name}/{model_name}_list.html', '{model_name}s': {model_name}s)"
    views_gen += f"\n\ndef {model_name}_detail(request, pk):"
    views_gen += f"\n    {model_name} = {model_name}.objects.get(pk=pk)"
    views_gen += f"\n    return render(request, '{app_name}/{model_name}_detail.html', '{model_name}': {model_name})"
    views_gen += f"\n    return render(request, '{app_name}/{model_name}_detail.html', '{model_name}': {model_name})"
    views_gen += f"\n\ndef {model_name}_create(request):"
    views_gen += f"\n    form = {model_name}Form()"
    views_gen += (
        f"\n    return render(request, '{app_name}/{model_name}_create.html', )"
    )
    views_gen += f"\n\ndef {model_name}_update(request, pk):"
    views_gen += f"\n    {model_name} = {model_name}.objects.get(pk=pk)"
    views_gen += f"\n    form = {model_name}Form(instance={model_name})"
    views_gen += f"\n    return render(request, '{app_name}/{model_name}_edit.html', 'form': 'form')"
    views_gen += f"\n\ndef {model_name}_delete(request, pk):"
    views_gen += f"\n    {model_name} = {model_name}.objects.get(pk=pk)"
    views_gen += f"\n    return render(request, '{app_name}/{model_name}_delete.html', '{model_name}': {model_name})"
    views_gen = html_escape(views_gen)

    # for forms.py
    forms_gen = f"class {model_name}Form(forms.ModelForm):"
    forms_gen += "\n    class Meta:"
    forms_gen += f"\n        model = {model_name}"
    forms_gen += "\n        fields = '__all__'"
    forms_gen = html_escape(forms_gen)

    # for html
    html_gen = f"<h1>{model_name} </h1>"
    html_gen += "\n<p>Hello world!</p>"
    html_gen = html_escape(html_gen)

    context_gen = {
        "urls_gen": urls_gen,
        "views_gen": views_gen,
        "forms_gen": forms_gen,
        "html_gen": html_gen,
    }

    return context_gen
