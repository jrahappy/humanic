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


APPT_DAYS = [
    (0, "Sunday"),
    (1, "Monday"),
    (2, "Tuesday"),
    (3, "Wednesday"),
    (4, "Thursday"),
    (5, "Friday"),
    (6, "Saturday"),
]

HOLIDAY_CATEGORY = [
    ("N", "National"),
    ("C", "Company"),
    ("P", "Personal"),
]

TERM_CATEGORY = [
    ("D", "Daily"),
    ("W", "Weekly"),
    ("M", "Monthly"),
    ("Y", "Yearly"),
]
WORKHOURS = [
    (7, "7"),
    (8, "8"),
    (9, "9"),
    (10, "10"),
    (11, "11"),
    (12, "12PM"),
    (13, "1"),
    (14, "2"),
    (15, "3"),
    (16, "4"),
    (17, "5"),
    (18, "6"),
]

CONTRACT_STATUS = [
    ("A", "Active"),
    ("I", "Inactive"),
    ("T", "Terminated"),
]
