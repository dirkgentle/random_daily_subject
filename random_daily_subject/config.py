import os


class AuthConfig:
    password = os.getenv("REDDIT_PWD")
    username = os.getenv("REDDIT_USERNAME")
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")


class BasicConfig:
    debug_mode = bool(os.getenv("DEBUG"))
    subreddit = "Uruguay" if not debug_mode else "test"

    logs_folder = "../logs"
    db_path = "sqlite:///../db/topics.db"
    json_folder = "../topics"
    topic_files = [
        {"path": f"{json_folder}/topics.json"},
        {"path": f"{json_folder}/holidays.json", "is_holiday": True},
        {"path": f"{json_folder}/special_days.json", "is_special": True},
    ]
