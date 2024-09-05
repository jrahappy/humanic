from django import template
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma
import os

register = template.Library()


@register.filter
def currency(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    # return "${}".format(intcomma(floatformat(value, 2)))
    return "{}".format(intcomma(floatformat(value, 0)))


@register.filter
def filename(value):
    return os.path.basename(value)
