import json
from datetime import datetime
from typing import List

import pytest
from moto import mock_dynamodb2

from random_daily_subject.config import TopicFile
from random_daily_subject.db_handler import DBHandler


@pytest.fixture
def db_handler() -> DBHandler:
    with mock_dynamodb2():
        db_handler = DBHandler()
        yield db_handler


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
def sample_topic():
    return dict(
        id="grmt",
        title="gourmet",
        count=0,
        is_holiday=False,
        is_special=False,
        is_active=True,
        bodies=[
            dict(id="grmt-01", count=0, is_active=True, text="El rincon culinario."),
            dict(id="grmt-02", count=2, is_active=True, text="Que cocinaste anoche?"),
            dict(id="grmt-03", count=2, is_active=True, text="Sample 3"),
            dict(id="grmt-04", count=4, is_active=True, text="Sample 4"),
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
def sample_holiday():
    return dict(
        id="nwyr", day=1, month=1, is_active=True, title=dict(title="de año nuevo"),
    )


@pytest.fixture
def sample_no_holiday():
    """This should not be a holiday in the db."""
    return dict(id="no-holiday", day=2, month=1)


@pytest.fixture
def sample_inactive_holiday():
    return dict(
        id="fake-hldy",
        day=5,
        month=1,
        is_active=False,
        title=dict(id="nwyr", title="fake holiday"),
    )


@pytest.fixture
def sample_submission():
    return dict(
        date=datetime(day=18, month=7, year=2020),
        weekday=6,
        title_id="grmt",
        body_id="grmt-01",
    )
