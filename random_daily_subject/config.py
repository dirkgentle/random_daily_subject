import os
from typing import Dict, Union

TopicFile = Dict[str, Union[str, bool]]


class AuthConfig:
    password = os.getenv("REDDIT_PWD")
    username = os.getenv("REDDIT_USERNAME")
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")


class BasicConfig:
    debug_mode = bool(os.getenv("DEBUG"))
    subreddit = "Uruguay" if not debug_mode else "test"

    logs_folder = "./logs"
    db_url = os.getenv("DB_URL")

    json_folder = "./topics"
    topic_files = [
        {"path": f"{json_folder}/topics.json"},
        {"path": f"{json_folder}/holidays.json", "is_holiday": True},
        {"path": f"{json_folder}/special_days.json", "is_special": True},
    ]

    weekday_names = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
    ]

    epilogue_text = (
        "\n\n*****\n\n"
        " *Another bot by \\/u/DirkGentle.*"
        " [Source.](https://github.com/dirkgentle/random_daily_subject)"
    )

    flair_text = "Discusion"
