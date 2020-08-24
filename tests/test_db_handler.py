import json
from datetime import datetime
from typing import List

from random_daily_subject.config import TopicFile
from random_daily_subject.db_handler import DBHandler


def test_load_topics(loaded_db: DBHandler, topic_files: List[TopicFile]) -> None:
    for topic_file in topic_files:
        with open(topic_file["path"]) as f:
            topics = json.load(f)

        is_holiday = topic_file.get("is_holiday", False)
        is_special = topic_file.get("is_special", False)

        for topic in topics:
            db_topic = loaded_db.topics_table.get_item(Key={"id": topic["id"]})["Item"]
            assert db_topic["title"] == topic["title"]
            assert db_topic["count"] == topic.get("count", 0)
            assert db_topic["is_holiday"] == is_holiday
            assert db_topic["is_special"] == is_special
            assert db_topic["is_active"] == topic.get("is_active", True)

            if is_holiday:
                assert db_topic["day"] == topic["day"]
                assert db_topic["month"] == topic["month"]

            for body in topic.get("bodies"):
                db_body = next(
                    db_body
                    for db_body in db_topic["bodies"]
                    if db_body["id"] == body["id"]
                )
                assert db_body is not None
                assert db_body["text"] == body["text"]
                assert db_body["is_active"] == body.get("is_active", True)
                assert db_body["count"] == body.get("count", 0)


def test_clean_topics(loaded_db: DBHandler, empty_files: List[TopicFile]) -> None:
    loaded_db.clean_topics(empty_files)

    scan_kwargs = {}
    all_topics = []
    done = False
    start_key = None
    while not done:
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key
        response = loaded_db.topics_table.scan(**scan_kwargs)
        all_topics += response.get("Items")
        start_key = response.get("LastEvaluatedKey", None)
        done = start_key is None

    all_bodies = [body for topic in all_topics for body in topic["bodies"]]

    assert all(not topic["is_active"] for topic in all_topics)
    assert all(not body["is_active"] for body in all_bodies)


def test_add_submission(loaded_db: DBHandler, sample_topic) -> None:
    sample_body = sample_topic["bodies"][0]
    date = datetime.now()

    old_topic = loaded_db.topics_table.get_item(Key={"id": sample_topic["id"]})["Item"]
    old_body = next(
        body for body in old_topic["bodies"] if body["id"] == sample_body["id"]
    )

    loaded_db.add_submission(sample_topic["id"], sample_body["id"], date)

    submission = loaded_db.submissions_table.get_item(Key={"date": date.isoformat()})[
        "Item"
    ]

    assert submission["title_id"] == sample_topic["id"]
    assert submission["body_id"] == sample_body["id"]
    assert submission["date"] == date.isoformat()
    assert submission["weekday"] == date.weekday()

    new_topic = loaded_db.topics_table.get_item(Key={"id": sample_topic["id"]})["Item"]
    new_body = next(
        body for body in new_topic["bodies"] if body["id"] == sample_body["id"]
    )

    assert new_topic["count"] == old_topic["count"] + 1
    assert new_body["count"] == old_body["count"] + 1


def test_is_date_holiday(
    loaded_db: DBHandler, sample_holiday, sample_no_holiday, sample_inactive_holiday,
) -> None:
    assert loaded_db.is_date_holiday(
        datetime(day=sample_holiday["day"], month=sample_holiday["month"], year=2020)
    )
    assert not loaded_db.is_date_holiday(
        datetime(
            day=sample_no_holiday["day"], month=sample_no_holiday["month"], year=2020
        )
    )
    assert not loaded_db.is_date_holiday(
        datetime(
            day=sample_inactive_holiday["day"],
            month=sample_inactive_holiday["month"],
            year=2020,
        )
    )


def test_get_day_holiday(loaded_db: DBHandler, sample_holiday) -> None:
    topic = loaded_db.get_date_holiday(
        datetime(day=sample_holiday["day"], month=sample_holiday["month"], year=2020)
    )

    assert topic["id"] == sample_holiday["id"]


def test_get_all_titles(loaded_db: DBHandler, topic_files: List[TopicFile]) -> None:
    all_db_titles = [title["id"] for title in loaded_db.get_all_titles()]
    all_json_titles = []

    for topic_file in topic_files:
        if topic_file.get("is_holiday") or topic_file.get("is_special"):
            continue

        with open(topic_file["path"]) as f:
            topics = json.load(f)

        all_json_titles += [topic["id"] for topic in topics]

        assert set(all_db_titles) == set(all_json_titles)


def test_get_title(loaded_db: DBHandler, sample_topic) -> None:
    topic = loaded_db.get_title(sample_topic["id"])

    assert topic["id"] == sample_topic["id"]
    assert topic["title"] == sample_topic["title"]


def test_get_all_bodies(loaded_db: DBHandler, sample_topic) -> None:
    all_bodies = loaded_db.get_all_bodies(sample_topic["id"])
    all_bodies = [body["id"] for body in all_bodies]
    sample_bodies = [body["id"] for body in sample_topic["bodies"]]

    assert set(all_bodies) == set(sample_bodies)


def test_get_body(loaded_db: DBHandler, sample_topic) -> None:
    sample_body = sample_topic["bodies"][0]
    body = loaded_db.get_body(sample_topic["id"], sample_body["id"])

    assert body["id"] == sample_body["id"]
    assert body["text"] == sample_body["text"]


def test_get_latest_submissions(db_with_history: DBHandler, sample_submission) -> None:
    n = 3
    latest_submissions = db_with_history.get_latest_submissions(n)

    assert len(latest_submissions) == n
    assert all(sub["title_id"] for sub in latest_submissions)
    assert all(sub["body_id"] for sub in latest_submissions)
    assert all(
        sub1["date"] > sub2["date"]
        for sub1, sub2 in zip(latest_submissions, latest_submissions[1:])
    )
