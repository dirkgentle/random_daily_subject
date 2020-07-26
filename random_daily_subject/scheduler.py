from datetime import datetime

import praw
from apscheduler.schedulers.blocking import BlockingScheduler

from random_daily_subject.bot import bot
from random_daily_subject.config import AuthConfig
from random_daily_subject.db_handler import DBHandler


sched = BlockingScheduler()


@sched.scheduled_job("cron", hour=8, minute=2)
def scheduled_job():
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
        date=date, reddit_client=reddit_client, debug_mode=True, db_handler=db_handler,
    )


if __name__ == "__main__":
    sched.start()
