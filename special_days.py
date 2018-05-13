import datetime


def week_number_in_month(date):
    return date.day // 7 + 1

def is_tuesday(date):
    if date.weekday() == 1:
        return 'rant'

def is_gnocchi_day(date):
    if date.day == 29:
        return 'noqui'

def is_mothers_day(date):
    date_is_mothers_day = (
        date.weekday() == 6 and date.month == 5 and
        week_number_in_month(date) == 2
    )
    if date_is_mothers_day:
        return 'mthrs'

def is_fathers_day(date):
    date_is_fathers_day = (
        date.weekday() == 6 and date.month == 7 and 
        week_number_in_month(date) == 2
    )
    if date_is_fathers_day:
        return 'fthrs'

def is_childrens_day(date):
    date_is_childrens_day = (
        date.weekday() == 6 and date.month == 8 and
        week_number_in_month(date) == 2
    )
    if date_is_childrens_day:
        return 'chldn'

special_day_checks = [
    is_mothers_day,
    is_fathers_day,
    is_childrens_day,
    is_tuesday,
    is_gnocchi_day,
]

def is_special_day(date=None):
    if date == None:
        date = datetime.datetime.today()

    for special_day_check in special_day_checks:
        title_id = special_day_check(date)
        if title_id:
            return title_id

