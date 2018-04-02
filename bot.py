import random
import datetime
import time
import traceback
import sys, getopt
import sqlite3

import praw

import login
import weekly_topics


def update_log(title, log_path): #para los comentarios que ya respondi
    conn = sqlite3.connect(log_path)
    c = conn.cursor()
    c.execute(
        'INSERT INTO submitted VALUES (NULL, ?, ?, ?)',
        (datetime.datetime.now(), datetime.date.today().weekday(), title))
    conn.commit()
    c.close()


def load_log(log_path, limit): #para los comentarios que ya respondi
    conn = sqlite3.connect(log_path)
    c = conn.cursor()
    c.execute(
        'SELECT title FROM submitted ORDER BY DATETIME(date) DESC LIMIT ?',
        (str(limit,)))
    log = [x[0] for x in c.fetchall()]
    c.close()
    return log

def output_log(text): #lo uso para ver el output del bot
    output_log_path = "output_log.txt"
    with open(output_log_path, 'a') as myLog:
        s = "[" +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
        s = s + text +  "\n"
        myLog.write(s)

def is_date_holiday(date):
    key = (date.month, date.day)
    return (key in weekly_topics.holidays), weekly_topics.holidays.get(key)

def is_today_holiday():
    return is_date_holiday(datetime.datetime.today())

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

        is_holiday, post = is_today_holiday()
        if is_holiday:
            today = post[0]
            body = post[1]
        elif datetime.datetime.today().weekday() == 1: #Es martes?
            today = "RANT"
            body = ("**DALE BO ES MARTES!** \n\n ¿COMO NO SE ESTAN QUEJANDO " 
                "YA? ¿TENGO QUE QUEJARME POR TODOS AHORA??? \n\n "
                "**(╯°□°）╯︵ ┻━┻)** ")
        elif datetime.datetime.today().day == 29:
            today = "ñoquis"
            body = ("Sus experiencias con el estado uruguayo. "
                "O podemos hablar de pasta. Como ustedes quieran.")
        else:
            log = load_log(log_path, log_limit)
            while True:
                today = random.SystemRandom().choice(list(weekly_topics.topics.keys()))
                if today not in log:
                    break
            body = weekly_topics.topics[today]
        if not debug_mode:
            update_log(today, log_path)
        else:
            update_log(today, log_path)
            print('Log: ' + str(log))
            print('Today: ' + today)

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
