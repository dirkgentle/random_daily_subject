import os


class RedditConfig:
    password = os.getenv("REDDIT_PWD")
    username = os.getenv("REDDIT_USERNAME")
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")


class BasicConfig:
    debug_mode = bool(os.getenv("DEBUG"))
