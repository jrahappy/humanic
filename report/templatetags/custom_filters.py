from django import template
import os

register = template.Library()


@register.filter(name="sum_values")
def sum_values(queryset, key):
    total = 0
    for item in queryset:
        # Check if the item is a dictionary
        if isinstance(item, dict):
            value = item.get(key, 0)
        else:
            # Use getattr for model instances or objects
            value = getattr(item, key, 0)

        # Ensure value is numeric before adding
        try:
            total += float(value)
        except (TypeError, ValueError):
            pass  # Ignore non-numeric values

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
    return value.split("/")[-1]
    # return os.path.basename(value)


@register.filter
def currency(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    # return "${}".format(intcomma(floatformat(value, 2)))
    return "{}".format(intcomma(floatformat(value, 0)))


@register.filter
def div_value(value, arg):
    try:
        value = float(value)
        arg = float(arg)
    except (ValueError, TypeError):
        return value
    if arg == 0:
        return 0
    return value / arg


@register.filter
def divide_by_60(value):
    try:
        return int(value // 60)
    except (ValueError, TypeError):
        return 0  # Return 0 if there's an error


@register.filter
def weekday_name(value):
    WEEKDAY_MAP = {
        1: "Sunday",
        2: "Monday",
        3: "Tuesday",
        4: "Wednesday",
        5: "Thursday",
        6: "Friday",
        7: "Saturday",
    }
    return WEEKDAY_MAP.get(value, "Unknown")


@register.filter
def handle_none(value):
    return value if value else ""


# @register.filter
# def int(value):
#     try:
#         value = int(value)
#     except (ValueError, TypeError):
#         return value
#     return "{:,}".format(value)
