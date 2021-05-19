from datetime import datetime

import pytest

from random_daily_subject import special_days


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=21, month=7, year=2020), "rant"),
        (datetime(day=22, month=7, year=2020), None),
    ],
)
def test_is_tuesday(date, result):
    assert special_days.is_tuesday(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=25, month=7, year=2020), None),
        (datetime(day=26, month=7, year=2020), "rndm"),
    ],
)
def test_is_sunday(date, result):
    assert special_days.is_sunday(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=27, month=9, year=2019), "dvrs"),
        (datetime(day=28, month=9, year=2018), "dvrs"),
        (datetime(day=29, month=9, year=2017), "dvrs"),
        (datetime(day=30, month=9, year=2016), "dvrs"),
        (datetime(day=25, month=9, year=2015), "dvrs"),
        (datetime(day=26, month=9, year=2014), "dvrs"),
        (datetime(day=18, month=7, year=2020), None),
    ],
)
def test_is_diversity_day(date, result):
    assert special_days.is_diversity_day(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=29, month=7, year=2020), "noqui"),
        (datetime(day=28, month=7, year=2020), None),
    ],
)
def test_is_gnocchi_day(date, result):
    assert special_days.is_gnocchi_day(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=29, month=11, year=2019), "blk_frdy"),
        (datetime(day=23, month=11, year=2018), "blk_frdy"),
        (datetime(day=24, month=11, year=2017), "blk_frdy"),
        (datetime(day=25, month=11, year=2016), "blk_frdy"),
        (datetime(day=27, month=11, year=2015), "blk_frdy"),
        (datetime(day=28, month=11, year=2014), "blk_frdy"),
        (datetime(day=18, month=7, year=2020), None),
    ],
)
def test_is_black_friday(date, result):
    assert special_days.is_black_friday(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=17, month=5, year=2020), "mthrs"),
        (datetime(day=12, month=5, year=2019), "mthrs"),
        (datetime(day=13, month=5, year=2018), "mthrs"),
        (datetime(day=14, month=5, year=2017), "mthrs"),
        (datetime(day=15, month=5, year=2016), "mthrs"),
        pytest.param(
            datetime(day=10, month=5, year=2015), "mthrs", marks=pytest.mark.xfail
        ),
        (datetime(day=12, month=7, year=2020), "fthrs"),
        (datetime(day=14, month=7, year=2019), "fthrs"),
        (datetime(day=15, month=7, year=2018), "fthrs"),
        (datetime(day=16, month=7, year=2017), "fthrs"),
        pytest.param(
            datetime(day=10, month=7, year=2016), "fhtrs", marks=pytest.mark.xfail
        ),
        (datetime(day=12, month=7, year=2015), "fthrs"),
        (datetime(day=16, month=8, year=2020), "chldn"),
        (datetime(day=18, month=8, year=2019), "chldn"),
        (datetime(day=12, month=8, year=2018), "chldn"),
        pytest.param(
            datetime(day=20, month=8, year=2017), "chldn", marks=pytest.mark.xfail
        ),
        pytest.param(
            datetime(day=21, month=8, year=2016), "chldn", marks=pytest.mark.xfail
        ),
        (datetime(day=16, month=8, year=2015), "chldn"),
        (datetime(day=1, month=2, year=2020), None),
    ],
)
def test_is_commercial_day(date, result):
    assert special_days.is_commercial_day(date) == result


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime(day=1, month=1, year=2020), None),
        (datetime(day=29, month=1, year=2020), "noqui"),
        (datetime(day=29, month=10, year=2019), "rant"),
        (datetime(day=29, month=11, year=2019), "blk_frdy"),
        (datetime(day=27, month=9, year=2019), "dvrs"),
        (datetime(day=15, month=7, year=2018), "fthrs"),
        (datetime(day=8, month=7, year=2018), "rndm"),
    ],
)
def test_is_special_day(date, result):
    assert special_days.is_special_day(date) == result
