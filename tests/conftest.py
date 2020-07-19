import json
from datetime import datetime
from typing import List

import pytest

from random_daily_subject.config import TopicFile
from random_daily_subject.db_handler import DBHandler
from random_daily_subject.models import Body, Holiday, Submission, Title


@pytest.fixture
def db_handler() -> DBHandler:
    db_handler = DBHandler("sqlite:///:memory:")
    return db_handler


@pytest.fixture
def topic_files() -> List[TopicFile]:
    return [
        {"path": "./tests/topics/topics.json"},
        {"path": "./tests/topics/holidays.json", "is_holiday": True},
        {"path": "./tests/topics/special_days.json", "is_special": True},
    ]


@pytest.fixture
def loaded_db(db_handler: DBHandler, topic_files: List[TopicFile]) -> DBHandler:
    db_handler.load_topics(topic_files)

    return db_handler


@pytest.fixture
def db_with_history(loaded_db: DBHandler, topic_files: List[TopicFile]) -> DBHandler:
    for topic_file in topic_files:
        if topic_file.get("is_holiday") or topic_file.get("is_special"):
            continue

        with open(topic_file["path"]) as f:
            topics = json.load(f)

        for topic in topics:
            loaded_db.add_submission(topic["id"], topic["bodies"][0]["id"])

    return loaded_db


@pytest.fixture
def sample_title() -> Title:
    return Title(
        id="grmt",
        title="gourmet",
        count=0,
        is_holiday=False,
        is_special=False,
        is_active=True,
        bodies=[
            Body(id="grmt-01", count=0, is_active=True, body="El rincon culinario."),
            Body(id="grmt-02", count=2, is_active=True, body="Que cocinaste anoche?"),
            Body(id="grmt-03", count=2, is_active=True, body="Sample 3"),
            Body(id="grmt-04", count=4, is_active=True, body="Sample 4"),
        ],
    )


@pytest.fixture
def empty_files() -> List[TopicFile]:
    return [
        {"path": "./tests/topics/empty.json"},
        {"path": "./tests/topics/empty.json", "is_holiday": True},
        {"path": "./tests/topics/empty.json", "is_special": True},
    ]


@pytest.fixture
def sample_holiday() -> Holiday:
    return Holiday(
        title_id="nwyr",
        day=1,
        month=1,
        is_active=True,
        title=Title(title="de año nuevo"),
    )


@pytest.fixture
def sample_no_holiday() -> Holiday:
    """This should not be a holiday in the db."""
    return Holiday(title_id="no-holiday", day=2, month=1)


@pytest.fixture
def sample_inactive_holiday() -> Holiday:
    return Holiday(
        title_id="fake-hldy",
        day=5,
        month=1,
        is_active=False,
        title=Title(id="nwyr", title="fake holiday"),
    )


@pytest.fixture
def sample_submission() -> Submission:
    return Submission(
        date=datetime(day=18, month=7, year=2020),
        weekday=6,
        title_id="grmt",
        body_id="grmt-01",
    )
