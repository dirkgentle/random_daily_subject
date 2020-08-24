from random_daily_subject import random_post
from random_daily_subject.db_handler import DBHandler


def test_choose_random_title(db_with_history: DBHandler) -> None:
    log_len = 2
    n_iters = 10

    random_choices = []
    for _ in range(n_iters):
        random_choices.append(random_post.choose_random_title(db_with_history, log_len))

    all_titles = [title["id"] for title in db_with_history.get_all_titles()]
    historical_titles = [
        submission["title_id"]
        for submission in db_with_history.get_latest_submissions(log_len)
    ]

    assert all(choice in all_titles for choice in random_choices)
    assert all(choice not in historical_titles for choice in random_choices)


def test_choose_random_body(db_with_history: DBHandler, sample_topic) -> None:
    n_iters = 10
    bodies = sample_topic["bodies"]

    random_choices = []
    for _ in range(n_iters):
        random_choices.append(
            random_post.choose_random_body(db_with_history, sample_topic["id"])
        )

    all_bodies = [body["id"] for body in bodies]
    count_avg = sum([body["count"] for body in bodies]) / len(bodies)
    invalid_bodies = [body["id"] for body in bodies if body["count"] > count_avg]

    assert all(choice in all_bodies for choice in random_choices)
    assert all(choice not in invalid_bodies for choice in random_choices)
