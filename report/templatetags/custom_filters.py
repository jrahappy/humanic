from django import template
import os

register = template.Library()


# @register.filter(name="sum_values")
# def sum_values(queryset, key):
#     total = 0
#     for item in queryset:
#         value = getattr(item, key, 0)
#         print(f"Item: {item}, Key: {key}, Value: {value}")  # Debug statement
#         total += value
#     print(f"Total: {total}")  # Debug statement
#     return total


@register.filter(name="sum_values")
def sum_values(queryset, key):
    total = 0
    for item in queryset:
        value = item.get(key, 0)  # Use dictionary access method
        # print(f"Item: {item}, Key: {key}, Value: {value}")  # Debug statement
        total += value
    # print(f"Total: {total}")  # Debug statement
    return total


@register.filter(name="sum_values_company")
def sum_values_company(queryset, key):
    total = 0
    for item in queryset:
        value = item.get(key, 0)  # Use dictionary access method
        # print(f"Item: {item}, Key: {key}, Value: {value}")  # Debug statement
        total += value
    # print(f"Total: {total}")  # Debug statement
    return total


@register.simple_tag(takes_context=True)
def break_loop(context):
    context["loop_break"] = True
    return ""


@register.filter
def filename(value):
    """Extracts the filename from a file path or URL."""
    return os.path.basename(value)
