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


def get_workhour_html(arr):
    html_arr = ""

    if arr is not None:
        if isinstance(arr, str):
            arr = [int(i) for i in ast.literal_eval(arr)]
            # arr = [int(i) if i.isdigit() else 99 for i in ast.literal_eval(arr)]
        else:
            arr = [int(i) for i in arr]

        start = end = arr[0]

        html_arr = ""
        for tooth in arr[1:] + [None]:
            if tooth == end + 1:
                end = tooth
            else:
                if start == end:
                    if start == 99:
                        html_arr += f"<span class='badge badge-info' style='margin-right:3px;' id='tooth-99'>Other</span>"
                    else:
                        html_arr += f"<span class='badge badge-info' style='margin-right:3px;' id='tooth-{start}'>{start}</span>"
                else:
                    html_arr += f"<span class='badge badge-info' style='margin-right:3px;' id='tooth-{start}-{end}'>{start}-{end}</span>"
                start = end = tooth

    return html_arr


APPT_DAYS = [
    ("0", "Sunday"),
    ("1", "Monday"),
    ("2", "Tuesday"),
    ("3", "Wednesday"),
    ("4", "Thursday"),
    ("5", "Friday"),
    ("6", "Saturday"),
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
    # (7, "7"),
    # (8, "8"),
    (9, "9"),
    (10, "10"),
    (11, "11"),
    (12, "12PM"),
    (13, "1"),
    (14, "2"),
    (15, "3"),
    (16, "4"),
    (17, "5"),
    (99, "All Day"),
]

CONTRACT_STATUS = [
    ("A", "Active"),
    ("P", "PartTime"),
    ("I", "Inactive"),
    ("T", "Terminated"),
]

OPPORTUNITY_CATEGORY = [
    ("Sale", "Sale"),
    ("Support", "Support"),
    ("Issue", "Issue"),
]

OPPORTUNITY_STAGE = [
    ("Potential", "Potential"),
    ("Qualified", "Qualified"),
    ("Working", "Working"),
    ("Won", "Won"),
    ("Pending", "Pending"),
    ("Lost", "Lost"),
]

GENDER = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]

REFER_STATUS = [
    ("Draft", "Draft"),
    ("Requested", "협진요청"),
    ("Interpreted", "1차판독완료"),
    ("Cosigned", "2차찬독완료"),
]
