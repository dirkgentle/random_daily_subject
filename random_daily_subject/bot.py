import sys
import traceback
from datetime import datetime
from getopt import getopt, GetoptError

import praw

import special_days
from config import AuthConfig, BasicConfig
from db_handler import DBHandler
from logger import output_log
from random_post import choose_random_body, choose_random_title


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
        title_id = db_handler.get_date_holiday(date)
    elif special_days.is_special_day(date):
        title_id = special_days.is_special_day(date)
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
        submission = reddit_client.subreddit(BasicConfig.subreddit).submit(
            title, selftext=body
        )
        # set flair
        template_id = next(
            x
            for x in submission.flair.choices()
            if x["flair_text"] == BasicConfig.flair_text
        )["flair_template_id"]
        submission.flair.select(template_id)


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
