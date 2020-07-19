from datetime import datetime

import pytest

from random_daily_subject.bot import bot
from random_daily_subject.db_handler import DBHandler


@pytest.mark.parametrize(
    "date",
    [
        datetime(day=1, month=1, year=2020),
        datetime(day=2, month=1, year=2020),
        datetime(day=7, month=1, year=2020),
    ],
)
def test_bot(db_with_history: DBHandler, date) -> None:
    bot(
        date,
        reddit_client=None,
        db_handler=db_with_history,
        debug_mode=True,
        log_limit=3,
    )
