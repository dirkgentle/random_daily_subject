import datetime
import getopt
import random
import sqlite3
import sys
import traceback

import praw

import db_handler
import login
import special_days


def update_log(cursor, title_id, comment_id):
    # para los comentarios que ya respondi
    db_handler.update_submitted(cursor, title_id, comment_id)


def load_log(cursor, limit):
    # para los comentarios que ya respondi
    aux = db_handler.get_latest_submissions(cursor, limit)
    return [x[0] for x in aux]


def output_log(text, debug_mode=False):
    # lo uso para ver el output del bot
    date_text = datetime.date.today().strftime('%Y_%m')
    output_log_path = './logs/' + date_text + '_output_log.txt'
    with open(output_log_path, 'a') as myLog:
        s = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']'
        s = s + text + '\n'
        myLog.write(s)
    if debug_mode:
        print(text)


def choose_random_title(c, log_limit=6):
    log = load_log(c, log_limit)

    c.execute('''SELECT id,count FROM titles WHERE
        is_active!=0 AND is_holiday==0 AND is_special==0''')
    options = [option for option in c.fetchall() if option[0] not in log]

    choosing_bag = []
    count_avg = sum([option[1] for option in options]) / len(options)
    for option in options:
        # favour those options that haven't come out so much
        multiplier = (
            1 + int(2 * (count_avg - option[1]))
            if option[1] < count_avg else 1
        )
        for _ in range(multiplier):
            choosing_bag.append(option[0])

    return random.choice(choosing_bag)


def choose_random_body(c, title_id):
    c.execute(
        'SELECT id,count FROM bodies WHERE is_active!=0 AND title_id=?',
        (title_id,)
    )
    options = [option for option in c.fetchall()]

    count_avg = sum([option[1] for option in options]) / len(options)
    choosing_bag = [option[0] for option in options if option[1] <= count_avg]

    return random.choice(choosing_bag)


days = [
    'Lunes',
    'Martes',
    'Miercoles',
    'Jueves',
    'Viernes',
    'Sabado',
    'Domingo'
    ]

epilogue_text = (
    '\n\n*****\n\n'
    ' *Another bot by \/u/DirkGentle.*'
    ' [Source.](https://github.com/dirkgentle/random_daily_subject)'
    )


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
        output_log('Comenzando el script', debug_mode)
        reddit = praw.Reddit(
            client_id=login.client_id,
            client_secret=login.client_secret,
            password=login.password,
            username=login.username,
            user_agent='testscript for /u/random_daily_subject'
        )

        conn = sqlite3.connect(log_path)
        c = conn.cursor()

        if db_handler.is_today_holiday(c):
            title_id = db_handler.is_today_holiday(c)[0]
        elif special_days.is_special_day():
            title_id = special_days.is_special_day()
        else:
            title_id = choose_random_title(c, 6)

        body_id = choose_random_body(c, title_id)
        today = db_handler.get_title(c, title_id)[0]
        body = db_handler.get_body(c, body_id)[0]

        if not debug_mode:
            update_log(c, title_id, body_id)
        else:
            print('Log: ' + str(load_log(c, log_limit)))

        title = days[datetime.datetime.today().weekday()] + ' ' + today + '.'
        body = body + epilogue_text
        output_log(title, debug_mode)
        output_log(body, debug_mode)

        if not debug_mode:
            submission = reddit.subreddit('Uruguay').submit(
                title, selftext=body
            )
            # set flair
            template_id = (
                next(
                    x for x in submission.flair.choices()
                    if x['flair_text'] == 'Discusión'
                )['flair_template_id']
            )
            submission.flair.select(template_id)

    except Exception as exception:
        output_log(str(exception))
        output_log(traceback.format_exc())
        if debug_mode:
            raise(exception)
    finally:
        conn.commit()
        c.close()
