import sys
import traceback
from datetime import datetime
from getopt import getopt, GetoptError

import praw

from random_daily_subject.config import AuthConfig, BasicConfig
from random_daily_subject.db_handler import DBHandler
from random_daily_subject.logger import output_log
from random_daily_subject.random_post import choose_random_body, choose_random_title
from random_daily_subject.special_days import is_special_day


def bot(
    date: datetime,
    reddit_client: praw.Reddit,
    db_handler: DBHandler,
    debug_mode: bool = False,
    log_limit: int = 6,
) -> None:
    """
    Main body for the Random Daily Subject bot.

    `date` is a datetime object for the date to run the bot.
    `reddit_client` is PRAW instance to interact with Reddit.
    `db_handler` is a DBHandler instance for interacting with the DB.
    `debug_mode` prints to STDOUT and does not modify the DB or post on Reddit
    `log_limit` is the number of previous days to retrieve from the DB to avoid repetition.
    """
    output_log("Starting script", debug_mode)

    if db_handler.is_date_holiday(date):
        title_id = db_handler.get_date_holiday(date).id
    elif is_special_day(date):
        title_id = is_special_day(date)
    else:
        title_id = choose_random_title(db_handler, log_limit)

    body_id = choose_random_body(db_handler, title_id)
    title = db_handler.get_title(title_id).title
    body = db_handler.get_body(body_id).body

    if debug_mode:
        print(f"Log: {db_handler.get_latest_submissions(log_limit)}")
    else:
        db_handler.add_submission(title_id, body_id)

    title = f"{BasicConfig.weekday_names[date.weekday()]} {title}."
    body = f"{body} {BasicConfig.epilogue_text}"
    output_log(title, debug_mode)
    output_log(body, debug_mode)

    if not debug_mode:
        subreddit = reddit_client.subreddit(BasicConfig.subreddit)
        # set flair
        template_id = next(
            t["id"]
            for t in subreddit.flair.link_templates
            if t["type"] == "richtext"
            and any(chunk.get("t") == BasicConfig.flair_text for chunk in t["richtext"])
        )

        _ = subreddit.submit(title, selftext=body, flair_id=template_id)


if __name__ == "__main__":
    log_limit = 6
    debug_mode = BasicConfig.debug_mode

    if not debug_mode:
        try:
            opts, args = getopt(sys.argv[1:], "d", "debug")
        except GetoptError:
            print("bot.py -d")
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-d", "--debug"):
                debug_mode = True

    try:
        date = datetime.today()
        reddit_client = praw.Reddit(
            client_id=AuthConfig.client_id,
            client_secret=AuthConfig.client_secret,
            password=AuthConfig.password,
            username=AuthConfig.username,
            user_agent="testscript for /u/random_daily_subject",
        )
        db_handler = DBHandler()

        bot(
            date=date,
            reddit_client=reddit_client,
            debug_mode=debug_mode,
            db_handler=db_handler,
        )
    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
        if debug_mode:
            raise (exception)
