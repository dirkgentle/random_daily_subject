import random
import datetime
import time
import traceback
import sys, getopt
import sqlite3

import praw

import login
import db_handler


def update_log(cursor, title_id, comment_id):
    # para los comentarios que ya respondi
    db_handler.update_submitted(cursor, title_id, comment_id)

def load_log(cursor, limit):
    # para los comentarios que ya respondi
    aux = db_handler.get_latest_submissions(cursor, limit)
    return [x[0] for x in aux]

def output_log(text):
    # lo uso para ver el output del bot
    output_log_path = "output_log.txt"
    with open(output_log_path, 'a') as myLog:
        s = "[" +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
        s = s + text +  "\n"
        myLog.write(s)

days = [
    'Lunes',
    'Martes',
    'Miercoles',
    'Jueves',
    'Viernes',
    'Sabado',
    'Domingo'
    ]


if __name__ == "__main__":

    log_path = 'topics.db'
    log_limit = 6
    debug_mode = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd', 'debug')
    except getopt.GetoptError:
        print('bot.py -d')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-d', '--debug'):
            debug_mode = True

    try:
        output_log('Comenzando el script')
        reddit = praw.Reddit(
            client_id = login.client_id,
            client_secret = login.client_secret,
            password = login.password,
            username = login.username,
            user_agent = 'testscript for /u/random_daily_subject')

        conn = sqlite3.connect(log_path)
        c = conn.cursor()

        title_id = db_handler.is_today_holiday(c)
        if title_id:
            title_id = title_id[0]
            today = db_handler.get_title(c, title_id)[0]
            [body, body_id] = db_handler.get_random_body(c, title_id)
        elif datetime.datetime.today().weekday() == 1: #Es martes?
            title_id = 'rant'
        elif datetime.datetime.today().day == 29:
            title_id = 'noqui'
        else:
            log = load_log(c, log_limit)
            while True:
                [title_id, today] = db_handler.get_random_title(c)
                if title_id not in log:
                    break

        [body_id, body] = db_handler.get_random_body(c, title_id)

        if not debug_mode:
            update_log(c, title_id, body_id)
        else:
            print('Log: ' + str(log))
            print('Today: ' + today)
            print('Body: ' + body)

        title = days[datetime.datetime.today().weekday()] \
                + ' de ' + today + '.'
        body = body + "\n\n*****\n\n"
        body = body + "*Another bot by \/u/DirkGentle.* "
        body = body + "[Source](https://github.com/dirkgentle/random_daily_subject)."
        output_log(title)
        output_log(body)
        if not debug_mode:
            reddit.subreddit('Uruguay').submit(title, selftext=body)

    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
        if debug_mode:
            raise(exception)
    finally:
        conn.commit()
        c.close()
