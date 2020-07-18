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
def empty_files() -> List[TopicFile]:
    return [
        {"path": "./tests/topics/empty.json"},
        {"path": "./tests/topics/empty.json", "is_holiday": True},
        {"path": "./tests/topics/empty.json", "is_special": True},
    ]


@pytest.fixture
def loaded_db(db_handler, topic_files) -> DBHandler:
    db_handler.load_topics(topic_files)
    return db_handler


def test_load_topics(loaded_db, topic_files):
    for topic_file in topic_files:
        with open(topic_file["path"]) as f:
            topics = json.load(f)

        is_holiday = topic_file.get("is_holiday", False)
        is_special = topic_file.get("is_special", False)

        for topic in topics:
            title = loaded_db.session.query(Title).filter_by(id=topic["id"]).one()
            assert title.title == topic["title"]
            assert title.count == topic.get("count", 0)
            assert title.is_holiday == is_holiday
            assert title.is_special == is_special
            assert title.is_active == topic.get("is_active", True)

            if is_holiday:
                holiday = (
                    loaded_db.session.query(Holiday)
                    .filter_by(title_id=topic["id"])
                    .one()
                )
                assert holiday.day == topic["day"]
                assert holiday.month == topic["month"]
                assert holiday.is_active == topic.get("is_active", True)

            for body in topic.get("bodies"):
                db_body = loaded_db.session.query(Body).filter_by(id=body["id"]).one()
                assert db_body.body == body["text"]
                assert db_body.title_id == topic["id"]
                assert db_body.is_active == body.get("is_active", True)


def test_clean_topics(loaded_db, empty_files):
    loaded_db.clean_topics(empty_files)

    assert all(not title.is_active for title in loaded_db.session.query(Title).all())
    assert all(not body.is_active for body in loaded_db.session.query(Body).all())
    assert all(
        not holiday.is_active for holiday in loaded_db.session.query(Holiday).all()
    )


def test_add_submission(loaded_db):
    title_id = "grmt"
    body_id = "grmt-01"
    date = datetime.now()

    old_title_count = (
        loaded_db.session.query(Title.count).filter_by(id=title_id).scalar()
    )
    old_body_count = loaded_db.session.query(Body.count).filter_by(id=body_id).scalar()

    loaded_db.add_submission(title_id, body_id, date)

    submission = loaded_db.session.query(Submission).filter_by(date=date).one()

    assert submission.title_id == title_id
    assert submission.body_id == body_id

    new_title_count = (
        loaded_db.session.query(Title.count).filter_by(id=title_id).scalar()
    )
    new_body_count = loaded_db.session.query(Body.count).filter_by(id=body_id).scalar()

    assert new_title_count == old_title_count + 1
    assert new_body_count == old_body_count + 1


def test_is_date_holiday(loaded_db):
    assert loaded_db.is_date_holiday(datetime(day=1, month=1, year=2020))
    # not a holiday
    assert not loaded_db.is_date_holiday(datetime(day=2, month=1, year=2020))
    # inactive holiday
    assert not loaded_db.is_date_holiday(datetime(day=5, month=1, year=2020))
