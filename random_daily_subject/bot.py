import random
import sys
import traceback
from datetime import datetime
from getopt import getopt, GetoptError

import praw

import special_days
from config import RedditConfig, BasicConfig
from db_handler import DatabaseHandler


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


def output_log(text, debug_mode=False):
    """
    Used to see the bot output.
    """
    date_text = datetime.today().strftime("%Y_%m")
    output_log_path = f"./logs/{date_text}_output_log.txt"
    with open(output_log_path, "a") as myLog:
        date_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s = f"[{date_text}] {text}\n"
        myLog.write(s)
    if debug_mode:
        print(text)


def choose_random_title(database, log_limit=6):
    log = database.get_latest_submissions(log_limit)
    all_titles = database.get_all_titles(get_counts=True)

    options = [title for title in all_titles if title[0] not in log]

    choosing_bag = []
    count_avg = sum([option[1] for option in options]) / len(options)
    for option in options:
        # favour those options that haven't come out so much
        multiplier = (
            1 + int(2 * (count_avg - option[1])) if option[1] < count_avg else 1
        )
        for _ in range(multiplier):
            choosing_bag.append(option[0])

    return random.choice(choosing_bag)


def choose_random_body(database, title_id):
    options = [option for option in database.get_all_bodies(title_id, get_counts=True)]

    count_avg = sum([option[1] for option in options]) / len(options)
    choosing_bag = [option[0] for option in options if option[1] <= count_avg]

    return random.choice(choosing_bag)


if __name__ == "__main__":
    log_path = "topics.db"
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
            client_id=RedditConfig.client_id,
            client_secret=RedditConfig.client_secret,
            password=RedditConfig.password,
            username=RedditConfig.username,
            user_agent="testscript for /u/random_daily_subject",
        )

        database = DatabaseHandler(log_path)

        if database.is_today_holiday():
            title_id = database.is_today_holiday()[0]
        elif special_days.is_special_day():
            title_id = special_days.is_special_day()
        else:
            title_id = choose_random_title(database, log_limit)

        body_id = choose_random_body(database, title_id)
        today = database.get_title(title_id)[0]
        body = database.get_body(body_id)[0]

        if not debug_mode:
            database.update_submitted(title_id, body_id)
        else:
            print(f"Log: {database.get_latest_submissions(log_limit)}")

        title = f"{WEEKDAY_NAMES[datetime.today().weekday()]} {today}."
        body = f"{body} {EPILOGUE_TEXT}"
        output_log(title, debug_mode)
        output_log(body, debug_mode)

        if not debug_mode:
            submission = reddit.subreddit("Uruguay").submit(title, selftext=body)
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