import calendar
from datetime import datetime, timedelta, date
from .models import ChoiceMaster
from django.utils import timezone


def get_year_calendar(year):
    months = []
    today = timezone.now().date()
    current_month = int(today.month)
    # 향후 3개월 달력만 보여주기
    current_12_months = range(current_month, current_month + 6)
    # print(current_12_months)
    flag_year = False
    for month in current_12_months:
        if month > 12:
            month -= 12
            if not flag_year:
                year += 1
                flag_year = True

        month_days = []
        _, num_days = calendar.monthrange(year, month)
        start_day = calendar.monthrange(year, month)[0]

        # Create padding for the start of the month
        start_day_padding = [""] * start_day

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

    # Get the number of days and the starting weekday for the month
    _, num_days = calendar.monthrange(year, month)
    start_day = calendar.monthrange(year, month)[0]

    # Create padding for the start of the month
    start_day_padding = [""] * start_day

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
    ("Requested", "검사요청"),
    ("Scheduled", "검사예약"),
    ("Cancelled", "검사취소"),
    ("Interpreted", "1차판독완료"),
    ("Cosigned", "2차판독완료"),
    ("Archive", "정산완료"),
]

TASK_STATUS = [
    ("Todo", "Todo"),
    ("Doing", "Doing"),
    ("Done", "Done"),
    ("Cancelled", "Cancelled"),
]
