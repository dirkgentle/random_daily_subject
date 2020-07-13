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


WEEKDAY_NAMES = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

EPILOGUE_TEXT = (
    "\n\n*****\n\n"
    " *Another bot by \/u/DirkGentle.*"
    " [Source.](https://github.com/dirkgentle/random_daily_subject)"
)

FLAIR_TEXT = "Discusion"


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
        output_log("Starting script", debug_mode)
        reddit = praw.Reddit(
            client_id=AuthConfig.client_id,
            client_secret=AuthConfig.client_secret,
            password=AuthConfig.password,
            username=AuthConfig.username,
            user_agent="testscript for /u/random_daily_subject",
        )

        database = DBHandler()
        today = datetime.today()

        if database.is_date_holiday(today):
            title_id = database.get_date_holiday(today)
        elif special_days.is_special_day():
            title_id = special_days.is_special_day()
        else:
            title_id = choose_random_title(database, log_limit)

        body_id = choose_random_body(database, title_id)
        today = database.get_title(title_id).title
        body = database.get_body(body_id).body

        database.add_submission(title_id, body_id)
        if debug_mode:
            print(f"Log: {database.get_latest_submissions(log_limit)}")

        title = f"{WEEKDAY_NAMES[datetime.today().weekday()]} {today}."
        body = f"{body} {EPILOGUE_TEXT}"
        output_log(title, debug_mode)
        output_log(body, debug_mode)

        if not debug_mode:
            submission = reddit.subreddit(BasicConfig.subreddit).submit(
                title, selftext=body
            )
            # set flair
            template_id = next(
                x for x in submission.flair.choices() if x["flair_text"] == FLAIR_TEXT
            )["flair_template_id"]
            submission.flair.select(template_id)

    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
        if debug_mode:
            raise (exception)
