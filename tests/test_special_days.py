from datetime import datetime

from random_daily_subject import special_days


def test_is_tuesday():
    tuesday = datetime(day=21, month=7, year=2020)
    assert special_days.is_tuesday(tuesday) == "rant"

    not_tuesday = datetime(day=22, month=7, year=2020)
    assert special_days.is_tuesday(not_tuesday) is None


def test_is_diversity_day():
    diversity_days = [
        datetime(day=27, month=9, year=2019),
        datetime(day=28, month=9, year=2018),
        datetime(day=29, month=9, year=2017),
        datetime(day=30, month=9, year=2016),
        datetime(day=25, month=9, year=2015),
        datetime(day=26, month=9, year=2014),
    ]
    assert all(special_days.is_diversity_day(date) == "dvrs" for date in diversity_days)

    not_diversity_day = datetime(day=18, month=7, year=2020)
    assert special_days.is_diversity_day(not_diversity_day) is None


def test_is_gnocchi_day():
    gnocchi = datetime(day=29, month=7, year=2020)
    assert special_days.is_gnocchi_day(gnocchi)

    not_gnocchi = datetime(day=28, month=7, year=2020)
    assert special_days.is_gnocchi_day(not_gnocchi) is None


def test_is_black_friday():
    black_fridays = [
        datetime(day=29, month=11, year=2019),
        datetime(day=23, month=11, year=2018),
        datetime(day=24, month=11, year=2017),
        datetime(day=25, month=11, year=2016),
        datetime(day=27, month=11, year=2015),
        datetime(day=28, month=11, year=2014),
    ]
    assert all(
        special_days.is_black_friday(date) == "blk_frdy" for date in black_fridays
    )

    not_black_friday = datetime(day=18, month=7, year=2020)
    assert special_days.is_black_friday(not_black_friday) is None


def test_is_commercial_day():
    mothers_days = [
        datetime(day=17, month=5, year=2020),
        datetime(day=12, month=5, year=2019),
        datetime(day=13, month=5, year=2018),
        datetime(day=14, month=5, year=2017),
        datetime(day=15, month=5, year=2016),
        # datetime(day=10, month=5, year=2015),
    ]
    assert all(special_days.is_commercial_day(date) == "mthrs" for date in mothers_days)

    fathers_days = [
        datetime(day=12, month=7, year=2020),
        datetime(day=14, month=7, year=2019),
        datetime(day=15, month=7, year=2018),
        datetime(day=16, month=7, year=2017),
        # datetime(day=10, month=7, year=2016),
        datetime(day=12, month=7, year=2015),
    ]
    assert all(special_days.is_commercial_day(date) == "fthrs" for date in fathers_days)

    childrens_day = [
        datetime(day=16, month=8, year=2020),
        datetime(day=18, month=8, year=2019),
        datetime(day=12, month=8, year=2018),
        # datetime(day=20, month=8, year=2017),
        # datetime(day=21, month=8, year=2016),
        datetime(day=16, month=8, year=2015),
    ]
    assert all(
        special_days.is_commercial_day(date) == "chldn" for date in childrens_day
    )

    is_nothing_day = datetime(day=1, month=2, year=2020)
    assert special_days.is_commercial_day(is_nothing_day) is None


def test_is_special_day():
    nothing_day = datetime(day=1, month=1, year=2020)
    assert special_days.is_special_day(nothing_day) is None

    gnocchi_day = datetime(day=29, month=1, year=2020)
    assert special_days.is_special_day(gnocchi_day)

    gnocchi_tuesday = datetime(day=29, month=10, year=2019)
    assert special_days.is_special_day(gnocchi_tuesday) == "rant"

    gnocchi_black_friday = datetime(day=29, month=11, year=2019)
    assert special_days.is_special_day(gnocchi_black_friday) == "blk_frdy"

    diversity_day = datetime(day=27, month=9, year=2019)
    assert special_days.is_special_day(diversity_day) == "dvrs"

    commercial_day = datetime(day=15, month=7, year=2018)
    assert special_days.is_special_day(commercial_day) == "fthrs"
