import calendar
from datetime import datetime, timedelta, date
from django.utils import timezone
from .choices import (
    APPT_DAYS,
    HOLIDAY_CATEGORY,
    TERM_CATEGORY,
    WORKHOURS,
    CONTRACT_STATUS,
    OPPORTUNITY_CATEGORY,
    OPPORTUNITY_STAGE,
    GENDER,
    REFER_STATUS,
    TASK_STATUS,
)


def get_year_calendar(year):
    months = []
    today = timezone.now().date()

    current_month = int(today.month)
    current_12_months = range(1, 13)  # Full year (January to December)

    flag_year = False
    for month in current_12_months:
        if month > 12:
            month -= 12
            if not flag_year:
                year += 1
                flag_year = True

        month_days = []
        start_day, num_days = calendar.monthrange(year, month)

        # Fix: Adjust start_day (Move Monday=0 → Sunday=0)
        adjusted_start_day = (start_day + 1) % 7  # Now Sunday is 0

        # Create padding for the start of the month
        start_day_padding = [""] * adjusted_start_day

        for day in range(1, num_days + 1):
            date = datetime(year, month, day).date()
            month_days.append({"day": day, "date": date, "is_today": date == today})

        months.append(
            {
                "name": calendar.month_name[month],
                "start_day_padding": start_day_padding,
                "days": month_days,
            }
        )
    return months


# 한달 달력 만들기 (해당 월만 업데이트하기 위해서 만듬)
def get_month_calendar(year, month):
    # Get today's date
    today = timezone.now().date()

    # Initialize the list for the current month
    amonth = []

    start_day, num_days = calendar.monthrange(year, month)

    # Fix: Adjust start_day (Move Monday=0 → Sunday=0)
    adjusted_start_day = (start_day + 1) % 7  # Now Sunday is 0

    # Create padding for the start of the month
    start_day_padding = [""] * adjusted_start_day

    # Collect day information
    month_days = []
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        month_days.append(
            {
                "day": day,
                "date": date,
                "is_today": date == today,
                "is_past": date < today,
            }
        )

    # Create the month structure with name and padding
    amonth.append(
        {
            "name": calendar.month_name[month],
            "start_day_padding": start_day_padding,
            "days": month_days,
        }
    )

    return amonth


def mychoices(choice_name):
    from .models import ChoiceMaster
    return ChoiceMaster.objects.filter(choice_name=choice_name).values_list("choice_value", "choice_label")


def get_specialty_choices():
    from .models import ChoiceMaster
    cho = ChoiceMaster.objects.filter(choice_name="SPECIALTY2").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_platform_choices():
    from .models import ChoiceMaster
    cho = ChoiceMaster.objects.filter(choice_name="PLATFORM").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_amodality_choices():
    from .models import ChoiceMaster
    cho = ChoiceMaster.objects.filter(choice_name="AMODALITY").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_ayear_choices():
    from .models import ChoiceMaster
    cho = ChoiceMaster.objects.filter(choice_name="AYEAR").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_amonth_choices():
    from .models import ChoiceMaster
    cho = ChoiceMaster.objects.filter(choice_name="AMONTH").order_by("choice_order")
    choices = []
    for c in cho:
        choices.append((c.choice_key, c.choice_value))
    return choices


def get_blog_category():
    from .models import ChoiceMaster
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
