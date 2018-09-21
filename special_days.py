import calendar
import datetime


def is_tuesday(date):
    if date.weekday() == 1:
        return 'rant'


def is_diversity_day(date):
    diversity_day = max(
        week[-3] for week in calendar.monthcalendar(date.year, 9)
    )
    if date.month == 9 and date.day == diversity_day:
        return 'dvrs'


def is_gnocchi_day(date):
    if date.day == 29:
        return 'noqui'


commercial_days = [
    {'code': 'mthrs', 'month': 5},
    {'code': 'fthrs', 'month': 7},
    {'code': 'chldn', 'month': 8}
]


def week_number_in_month(date):
    return date.day // 7 + 1


def is_commercial_day(date):
    first_month_day = date.replace(day=1)
    # if the first 10th of the month is after the second weekend
    # the holiday is offset
    offset = (
        0 if first_month_day.weekday() < 3 else 1
    )

    for commercial_day in commercial_days:
        date_is_commercial_day = (
            date.weekday() == 6 and date.month == commercial_day['month']
            and week_number_in_month(date) == 2 + offset
        )
        if date_is_commercial_day:
            return commercial_day['code']


special_day_checks = [
    is_commercial_day,
    is_diversity_day,
    is_tuesday,
    is_gnocchi_day,
]


def is_special_day(date=None):
    if date is None:
        date = datetime.datetime.today()

    for special_day_check in special_day_checks:
        title_id = special_day_check(date)
        if title_id:
            return title_id
