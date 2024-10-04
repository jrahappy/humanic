from .models import ChoiceMaster


def mychoices(choice_name):
    cho = ChoiceMaster.objects.filter(choice_name=choice_name).order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_specialty_choices():
    cho = ChoiceMaster.objects.filter(choice_name="SPECIALTY2").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_platform_choices():
    cho = ChoiceMaster.objects.filter(choice_name="PLATFORM").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_amodality_choices():
    cho = ChoiceMaster.objects.filter(choice_name="AMODALITY").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_ayear_choices():
    cho = ChoiceMaster.objects.filter(choice_name="AYEAR").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_amonth_choices():
    cho = ChoiceMaster.objects.filter(choice_name="AMONTH").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_blog_category():
    cho = ChoiceMaster.objects.filter(choice_name="BLOG_CATEGORY").order_by(
        "choice_order"
    )
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices
