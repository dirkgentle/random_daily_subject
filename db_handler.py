import sqlite3
import datetime

import weekly_topics


def up_db(db_name):
    create_db(db_name)
    clean_db(db_name)
    load_topics(db_name)


def create_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS titles (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        is_holiday INTEGER,
        is_special INTEGER,
        is_active INTEGER
        )''') # is_xxx == 0 if not xxx, true for other cases
    c.execute('''CREATE TABLE IF NOT EXISTS bodies (
        id INTEGER PRIMARY KEY,
        body TEXT NOT NULL,
        title_id INTEGER NOT NULL,
        is_active INTEGER,
        FOREIGN KEY(title_id) REFERENCES titles(id)
        )''')
    c.execute('''CREATE TABLE IF NOT EXISTS submitted (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        weekday INTEGER,
        title_id INTEGER NOT NULL,
        body_id INTEGER,
        FOREIGN KEY(title_id) REFERENCES titles(id),
        FOREIGN KEY(body_id) REFERENCES bodies(id)
        )''')
    c.execute('''CREATE TABLE IF NOT EXISTS holidays (
        id INTEGER PRIMARY KEY,
        day INTEGER NOT NULL,
        month INTEGER,
        title_id INTEGER NOT NULL,
        FOREIGN KEY(title_id) REFERENCES titles(id)
        )''')
 
    conn.commit()
    c.close()


def load_topics(db_name): #from weeky_topics.py
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for topic in weekly_topics.topics.keys():
        title_id = update_title(c, topic, 0, 0)
        for body in weekly_topics.topics[topic]:
            update_body(c, body, title_id)

    for day, month in weekly_topics.holidays.keys():
        title = weekly_topics.holidays[(day,month)][0]
        body = weekly_topics.holidays[(day,month)][1]

        title_id = update_title(c, title, 1, 0)
        update_body(c, body, title_id)
        c.execute('INSERT INTO holidays VALUES (NULL, ?, ?, ?)',
            (day, month, title_id))

    for topic in weekly_topics.special_days.keys():
        title_id = update_title(c, topic, 0, 1)
        for body in weekly_topics.special_days[topic]:
            update_body(c, body, title_id)

    conn.commit()
    c.close()


def update_title(cursor, title, is_holiday, is_special):
    cursor.execute('SELECT * FROM titles WHERE title=?', (title,))
    db_topic = cursor.fetchone()
    if not db_topic:
        cursor.execute('INSERT INTO titles VALUES (NULL, ?, ?, ?, 1)',
            (title, is_holiday, is_special))
    elif db_topic[4] == 0:
        cursor.execute('UPDATE titles SET is_active=1 WHERE id=?',
            (db_topic[0]))
    return cursor.lastrowid


def update_body(cursor, body, title_id):
    cursor.execute('SELECT * FROM bodies WHERE title_id=?', (title_id,))
    db_body = cursor.fetchone()
    if not db_body:
        cursor.execute('INSERT INTO bodies VALUES (NULL, ?, ?, 1)',
            (body, title_id))
    elif db_body[3] == 0:
        cursor.execute('UPDATE bodies SET is_active=1 WHERE id=?',
            (db_body[0]))


def update_submitted(cursor, title_id, body_id=None):
    cursor.execute('INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)',
        (datetime.datetime.now(),datetime.date.today().weekday(),title_id,
         body_id,))


#db reading
def is_date_holiday(cursor, date):
    cursor.execute('SELECT title_id FROM holidays WHERE (day,month)=(?,?)',
        (date.day, date.month,))
    return cursor.fetchone()

def is_today_holiday(cursor):
    return is_date_holiday(cursor, datetime.datetime.today())

def get_latest_submissions(cursor, n=6):
    cursor.execute(
        'SELECT title_id FROM submitted ORDER BY DATETIME(date) DESC LIMIT ?',
        (str(n)))
    return cursor.fetchall()

def get_title(cursor, title_id):
    cursor.execute('SELECT title FROM titles WHERE id=?', (title_id,))
    return cursor.fetchone()

def get_random_submission(cursor):
    [title_id, title] = get_random_title(cursor)
    [body_id, body] = get_random_body(cursor, title_id)
    return (title_id, title, body_id, body)

def get_random_title(cursor):
    cursor.execute(
        '''SELECT id, title FROM titles
            WHERE is_holiday = 0 AND is_special = 0 AND is_active != 0
            ORDER BY RANDOM() LIMIT 1''',)
    return cursor.fetchone()

def get_random_body(cursor, title_id):
    cursor.execute(
        '''SELECT id, body FROM bodies
            WHERE title_id = ? AND is_active != 0
            ORDER BY RANDOM() LIMIT 1''',
            (str(title_id),))
    return cursor.fetchone()


#db cleaning
def clean_db(db_name):
    clean_titles(db_name)
    clean_bodies(db_name)

def clean_titles(db_name):
    all_keys = list(weekly_topics.topics)
    all_keys += [x[0] for x in weekly_topics.holidays.values()]
    all_keys += list(weekly_topics.special_days)
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT id,title FROM titles WHERE is_active!=0')
    titles = c.fetchall()
    for title in titles:
        if title[1] not in all_keys:
            c.execute('UPDATE titles SET is_active=0 WHERE id=?', (title[0],))

    conn.commit()
    c.close()

def clean_bodies(db_name): 
    all_bodies = [body for bodies in weekly_topics.topics.values()
                       for body in bodies]
    all_bodies += [x[1] for x in weekly_topics.holidays.values()]
    all_bodies += [body for bodies in weekly_topics.special_days.values()
                        for body in bodies]
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT id,body FROM bodies WHERE is_active!=0')
    bodies = c.fetchall()
    for body in bodies:
        if body[1] not in all_bodies:
            c.execute('UPDATE bodies SET is_active=0 WHERE id=?', (body[0],))

    conn.commit()
    c.close()

#para imprimir la base de datos en pantalla
def print_tables(db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(table_name)) # insecure!!! debug only
    out = c.fetchall()
    conn.commit()
    c.close()
    return out

def print_topics(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT * FROM titles')
    titles = c.fetchall()
    for title in titles:
        print('***************')
        print(title[1])
        
        if title[2]:
            print('Es feriado!')
            c.execute('SELECT * FROM holidays WHERE title_id=?',(title[0],))
            date = c.fetchone()
            print('Día ' + str(date[2]) + ' del mes ' + str(date[1]))
        
        if title[3]:
            print('Es un día especial')

        c.execute('SELECT * FROM bodies WHERE title_id=?',(title[0],))
        bodies = c.fetchall()
        for body in bodies:
            print(body[1])
    print('***************')

    conn.commit()
    c.close()

def print_submitted(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT * from submitted')
    submitted = c.fetchall()
    for submission in submitted:
        print('***************')
        print(str(submission[1]) + ' wday = ' + str(submission[2]))
        c.execute('SELECT title FROM titles WHERE id=?', (submission[3],))
        print(c.fetchone()[0])
        if submission[4]:
            c.execute('SELECT body FROM bodies WHERE id=?', (submission[4],))
            print(c.fetchone()[0])
    print('***************')

    conn.commit()
    c.close()


# Para migrar los datos viejos
def migrate_log_to_db(log_path, db_name, already_posted_today):
    with open(log_path) as old_log:
        log = [x.strip('\n') for x in old_log.readlines()]
    log = reversed(log)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    for i, topic in enumerate(log):
        print(topic)
        c.execute('SELECT id FROM titles WHERE title=?',(topic,))
        title_id = c.fetchone()[0]
        c.execute('SELECT id FROM bodies WHERE title_id=?',(title_id,))
        body_id = c.fetchall()[0][0]

        if already_posted_today:
            topic_date = (datetime.date.today() - datetime.timedelta(days=i))
        else:
            topic_date = (datetime.date.today() - datetime.timedelta(days=i+1))
        topic_weekday = topic_date.weekday()

        c.execute('INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)',
            (topic_date, topic_weekday, title_id , body_id))

    conn.commit()
    c.close()
