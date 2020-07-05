from calendar import monthcalendar
from datetime import datetime, timedelta


def is_tuesday(date):
    if date.weekday() == 1:
        return "rant"


def is_diversity_day(date):
    diversity_day = max(week[-3] for week in monthcalendar(date.year, 9))
    if date.month == 9 and date.day == diversity_day:
        return "dvrs"


def is_gnocchi_day(date):
    if date.day == 29:
        return "noqui"


def is_black_friday(date):
    """
    Black Friday is the day after thanksgiving (fourth Thursday of November)
    """
    november_calendar = monthcalendar(date.year, 11)
    thanksgiving_cal_day = (
        november_calendar[3][-4]
        if november_calendar[0][-4]
        else november_calendar[4][-4]
    )
    thanksgiving = datetime(year=date.year, month=11, day=thanksgiving_cal_day)
    black_friday = thanksgiving + timedelta(days=1)

    if date.month == black_friday.month and date.day == black_friday.day:
        return "blk_frdy"


commercial_days = [
    {"code": "mthrs", "month": 5},
    {"code": "fthrs", "month": 7},
    {"code": "chldn", "month": 8},
]


def week_number_in_month(date):
    return (date.day - 1) // 7 + 1


def is_commercial_day(date):
    first_month_day = date.replace(day=1)
    # if the first 10th of the month is after the second weekend
    # the holiday is offset
    offset = 0 if first_month_day.weekday() < 3 else 1

    for commercial_day in commercial_days:
        date_is_commercial_day = (
            date.weekday() == 6
            and date.month == commercial_day["month"]
            and week_number_in_month(date) == 2 + offset
        )
        if date_is_commercial_day:
            return commercial_day["code"]


SPECIAL_DAY_CHECKS = [
    is_commercial_day,
    is_diversity_day,
    is_black_friday,
    is_tuesday,
    is_gnocchi_day,
]


def is_special_day(date=None):
    if date is None:
        date = datetime.today()

    for special_day_check in SPECIAL_DAY_CHECKS:
        title_id = special_day_check(date)
        if title_id:
            return title_id
