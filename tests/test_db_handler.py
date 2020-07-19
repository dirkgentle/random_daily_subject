import json
from datetime import datetime
from typing import List

import pytest

from random_daily_subject.config import TopicFile
from random_daily_subject.db_handler import DBHandler
from random_daily_subject.models import Body, Holiday, Submission, Title


def test_load_topics(loaded_db: DBHandler, topic_files: List[TopicFile]) -> None:
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


def test_clean_topics(loaded_db: DBHandler, empty_files: List[TopicFile]) -> None:
    loaded_db.clean_topics(empty_files)

    assert all(not title.is_active for title in loaded_db.session.query(Title).all())
    assert all(not body.is_active for body in loaded_db.session.query(Body).all())
    assert all(
        not holiday.is_active for holiday in loaded_db.session.query(Holiday).all()
    )


def test_add_submission(loaded_db: DBHandler, sample_title: Title) -> None:
    sample_body = sample_title.bodies[0]
    date = datetime.now()

    old_title_count = (
        loaded_db.session.query(Title.count).filter_by(id=sample_title.id).scalar()
    )
    old_body_count = (
        loaded_db.session.query(Body.count).filter_by(id=sample_body.id).scalar()
    )

    loaded_db.add_submission(sample_title.id, sample_body.id, date)

    submission = loaded_db.session.query(Submission).filter_by(date=date).one()

    assert submission.title_id == sample_title.id
    assert submission.body_id == sample_body.id
    assert submission.date == date
    assert submission.weekday == date.weekday()

    new_title_count = (
        loaded_db.session.query(Title.count).filter_by(id=sample_title.id).scalar()
    )
    new_body_count = (
        loaded_db.session.query(Body.count).filter_by(id=sample_body.id).scalar()
    )

    assert new_title_count == old_title_count + 1
    assert new_body_count == old_body_count + 1


def test_is_date_holiday(
    loaded_db: DBHandler,
    sample_holiday: Holiday,
    sample_no_holiday: Holiday,
    sample_inactive_holiday: Holiday,
) -> None:
    assert loaded_db.is_date_holiday(
        datetime(day=sample_holiday.day, month=sample_holiday.month, year=2020)
    )
    assert not loaded_db.is_date_holiday(
        datetime(day=sample_no_holiday.day, month=sample_no_holiday.month, year=2020)
    )
    assert not loaded_db.is_date_holiday(
        datetime(
            day=sample_inactive_holiday.day,
            month=sample_inactive_holiday.month,
            year=2020,
        )
    )


def test_get_day_holiday(loaded_db: DBHandler, sample_holiday) -> None:
    title = loaded_db.get_date_holiday(
        datetime(day=sample_holiday.day, month=sample_holiday.month, year=2020)
    )

    assert title.id == sample_holiday.title_id


def test_get_all_titles(loaded_db: DBHandler, topic_files: List[TopicFile]) -> None:
    all_db_titles = loaded_db.get_all_titles()
    all_db_titles = [title.id for title in all_db_titles]
    all_json_titles = []

    for topic_file in topic_files:
        if topic_file.get("is_holiday") or topic_file.get("is_special"):
            continue

        with open(topic_file["path"]) as f:
            topics = json.load(f)

        all_json_titles += [topic["id"] for topic in topics]

        assert set(all_db_titles) == set(all_json_titles)


def test_get_title(loaded_db: DBHandler, sample_title: Title) -> None:
    title = loaded_db.get_title(sample_title.id)

    assert title.id == sample_title.id
    assert title.title == sample_title.title


def test_get_all_bodies(loaded_db: DBHandler, sample_title: Title) -> None:
    all_bodies = loaded_db.get_all_bodies(sample_title.id)
    all_bodies = [body.id for body in all_bodies]
    sample_bodies = [body.id for body in sample_title.bodies]

    assert set(all_bodies) == set(sample_bodies)


def test_get_body(loaded_db: DBHandler, sample_title: Title) -> None:
    sample_body = sample_title.bodies[0]
    body = loaded_db.get_body(sample_body.id)

    assert body.id == sample_body.id
    assert body.body == sample_body.body


def test_get_latest_submissions(
    db_with_history: DBHandler, sample_submission: Submission
) -> None:
    n = 3
    latest_submissions = db_with_history.get_latest_submissions(n)

    assert len(latest_submissions) == n
    assert all(isinstance(sub, Submission) for sub in latest_submissions)
    assert all(
        sub1.date > sub2.date
        for sub1, sub2 in zip(latest_submissions, latest_submissions[1:])
    )
