import ast
from django import template
from django.utils import timezone
import datetime

register = template.Library()


@register.filter(name="trim")
def trim(value):
    """Removes leading and trailing whitespace from the string."""
    return value.strip()


@register.filter
def is_older_than_24_hours(value):
    """
    주어진 datetime이 현재 시각으로부터 24시간이 지났는지 확인합니다.
    """
    if not value:
        return False
    now = timezone.now()
    return value < now - datetime.timedelta(hours=24)


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
    # WEEKDAY_MAP = {
    #     "0": "Sunday",
    #     "1": "Monday",
    #     "2": "Tuesday",
    #     "3": "Wednesday",
    #     "4": "Thursday",
    #     "5": "Friday",
    #     "6": "Saturday",
    # }
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


@register.filter(name="div")
def div(value, arg):
    try:
        return float(value) / float(arg) * 100
    except (ValueError, ZeroDivisionError):
        return None


@register.filter(name="get_dict")
def get_dict(dictionary, key):
    """Retrieve a value from a dictionary using a key, or return an empty list if key is missing."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return None


@register.filter
def get(dictionary, key):
    try:
        return dictionary.get(key)
    except (TypeError, AttributeError):
        return None


@register.filter
def get_item(dictionary, key):
    """Fetches the value from a dictionary with a dynamic key."""
    return dictionary.get(str(key), [])


@register.filter
def keys(dictionary):
    """Returns the keys of a dictionary as a list."""
    if isinstance(dictionary, dict):
        return list(dictionary.keys())
    return []


@register.filter
def get_key_from_value(choices, value):
    """Fetches the key from a choices tuple based on the value."""
    for key, val in choices:
        if val == value:
            return key
    return None


@register.filter
def get_val_from_value(choices, value):
    """Fetches the key from a choices tuple based on the value."""
    for key, val in choices:
        if val == value:
            return val
    return None


@register.filter
def get_workhour_short(arr):
    html_arr = ""
    if arr is not None:
        if isinstance(arr, str):
            arr = [int(i) for i in ast.literal_eval(arr)]
            # arr = [int(i) if i.isdigit() else 99 for i in ast.literal_eval(arr)]
        else:
            arr = [int(i) for i in arr]

        if not arr:  # Check if the list is empty
            return html_arr

        start = end = arr[0]

        for hr in arr[1:] + [None]:
            if hr == end + 1:
                end = hr
            else:
                if start == end:
                    if start == 99:
                        html_arr += "<span class='badge badge-info text-white font-semibold'>All Day</span>"
                    else:
                        html_arr += f"<span class='badge badge-info text-white font-semibold'>Hrs: {str(start)}</span>"
                else:
                    html_arr += f"<span class='badge badge-info text-white font-semibold'>Hrs: {start}-{end}</span>"
                start = end = hr

    return html_arr


# @register.filter
# def int(value):
#     try:
#         value = int(value)
#     except (ValueError, TypeError):
#         return value
#     return "{:,}".format(value)
