import datetime
import getopt
import random
import sys
import traceback

import praw

import login
import special_days
from db_handler import DatabaseHandler


def output_log(text, debug_mode=False):
    # lo uso para ver el output del bot
    date_text = datetime.date.today().strftime("%Y_%m")
    output_log_path = "./logs/{}_output_log.txt".format(date_text)
    with open(output_log_path, "a") as myLog:
        s = "[{}] {}\n".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text
        )
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


days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

epilogue_text = (
    "\n\n*****\n\n"
    " *Another bot by \/u/DirkGentle.*"
    " [Source.](https://github.com/dirkgentle/random_daily_subject)"
)


if __name__ == "__main__":
    log_path = "topics.db"
    log_limit = 6
    debug_mode = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d", "debug")
    except getopt.GetoptError:
        print("bot.py -d")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            debug_mode = True

    try:
        output_log("Comenzando el script", debug_mode)
        reddit = praw.Reddit(
            client_id=login.client_id,
            client_secret=login.client_secret,
            password=login.password,
            username=login.username,
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
            print("Log: {}".format(database.get_latest_submissions(log_limit)))

        title = "{} {}.".format(days[datetime.datetime.today().weekday()], today)
        body = "{} {}".format(body, epilogue_text)
        output_log(title, debug_mode)
        output_log(body, debug_mode)

        if not debug_mode:
            submission = reddit.subreddit("Uruguay").submit(title, selftext=body)
            # set flair
            template_id = next(
                x for x in submission.flair.choices() if x["flair_text"] == "Discusión"
            )["flair_template_id"]
            submission.flair.select(template_id)

    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
        if debug_mode:
            raise (exception)
