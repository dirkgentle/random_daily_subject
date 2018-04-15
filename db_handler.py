import sqlite3
import datetime
import json


def up_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    create_tables_db(c)
    clean_db(c)
    load_topics(c)

    conn.commit()
    c.close()

def create_tables_db(c):
    c.execute('''CREATE TABLE IF NOT EXISTS titles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        count INTEGER,
        is_holiday INTEGER,
        is_special INTEGER,
        is_active INTEGER
        )''') # is_xxx == 0 if not xxx, true for other cases
    c.execute('''CREATE TABLE IF NOT EXISTS bodies (
        id TEXT PRIMARY KEY,
        body TEXT NOT NULL,
        count INTEGER,
        title_id INTEGER NOT NULL,
        is_active INTEGER,
        FOREIGN KEY(title_id) REFERENCES titles(id)
        )''')
    c.execute('''CREATE TABLE IF NOT EXISTS submitted (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        weekday INTEGER,
        title_id TEXT NOT NULL,
        body_id TEXT,
        FOREIGN KEY(title_id) REFERENCES titles(id),
        FOREIGN KEY(body_id) REFERENCES bodies(id)
        )''')
    c.execute('''CREATE TABLE IF NOT EXISTS holidays (
        title_id TEXT PRIMARY KEY,
        day INTEGER NOT NULL,
        month INTEGER,
        FOREIGN KEY(title_id) REFERENCES titles(id)
        )''')


def load_topics(c):
    # c is the db cursor

    json_data = open('topics/topics.json').read()
    topics = json.loads(json_data)
    for topic in topics:
        update_title(c, topic)
        for body in topic.get('bodies'):
            update_body(c, body, topic['id'])

    json_data = open('topics/holidays.json').read()
    holidays = json.loads(json_data)
    for topic in holidays:
        update_title(c, topic, 1)
        update_holiday(c, topic)
        for body in topic.get('bodies'):
            update_body(c, body, topic['id'])

    json_data = open('topics/special_days.json').read()
    special_days = json.loads(json_data)
    for topic in special_days:
        update_title(c, topic, 0, 1)
        for body in topic.get('bodies'):
            update_body(c, body, topic['id'])

# update the database
def update_title(cursor, topic, is_holiday=0, is_special=0):
    cursor.execute('SELECT is_active FROM titles WHERE id=?', (topic['id'],))
    db_topic = cursor.fetchone()
    if not db_topic:
        cursor.execute(
            'INSERT INTO titles VALUES (?, ?, ?, ?, ?, 1)', (
                topic['id'],
                topic['title'],
                topic['count'],
                is_holiday,
                is_special
            )
        )
    else:
        cursor.execute('''UPDATE titles SET
            title=?,is_holiday=?,is_special=?,is_active=1 WHERE id=?''', (
                topic['title'],
                is_holiday,
                is_special,
                topic['id']
            )
        )
    return cursor.lastrowid

def update_body(cursor, body, title_id):
    cursor.execute('SELECT is_active FROM bodies WHERE id=?', (body['id'],))
    db_body = cursor.fetchone()
    if not db_body:
        cursor.execute('INSERT INTO bodies VALUES (?, ?, ?, ?, 1)',
            (body['id'], body['text'], body['count'], title_id))
    elif db_body[0] == 0:
        cursor.execute('''UPDATE bodies SET
            text=?,title_id=?,is_active=1 WHERE id=?''', (
                body['text'],
                title_id,
                body['id']
            )
        )

def update_submitted(cursor, title_id, body_id=None):
    cursor.execute('INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)',
        (datetime.datetime.now(),datetime.date.today().weekday(),title_id,
         body_id,))
    cursor.execute('UPDATE titles SET count = count + 1 WHERE id=?',
        (title_id,))
    if body_id:
        cursor.execute('UPDATE bodies SET count = count + 1 WHERE id=?',
            (body_id,))

def update_holiday(cursor, topic):
    cursor.execute('SELECT * FROM holidays WHERE title_id=?', (topic['id'],))
    db_topic = cursor.fetchone()
    if not db_topic:
        cursor.execute('INSERT INTO holidays VALUES (?, ?, ?)',
            (topic['id'], topic['day'], topic['month'],))


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

def get_title_id(cursor, title):
    cursor.execute('SELECT id FROM titles WHERE title LIKE ?',
        (title,))
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

def get_body(cursor, body_id):
    cursor.execute('SELECT body FROM bodies WHERE id=?', (body_id,))
    return cursor.fetchone()

def get_random_body(cursor, title_id):
    cursor.execute(
        '''SELECT id, body FROM bodies
            WHERE title_id = ? AND is_active != 0
            ORDER BY RANDOM() LIMIT 1''',
            (str(title_id),))
    return cursor.fetchone()


#db cleaning
def clean_db(c):
    # c is a db cursor
    clean_titles(c)
    clean_bodies(c)

def clean_titles(c):
    # c is a db cursor
    all_keys = []

    json_data = open('topics/topics.json').read()
    topics = json.loads(json_data)
    all_keys += [topic['id'] for topic in topics]

    json_data = open('topics/holidays.json').read()
    topics = json.loads(json_data)
    all_keys += [topic['id'] for topic in topics]
    
    json_data = open('topics/special_days.json').read()
    topics = json.loads(json_data)
    all_keys += [topic['id'] for topic in topics]

    c.execute('SELECT id FROM titles WHERE is_active!=0')
    title_ids = c.fetchall()
    for title_id in title_ids:
        if title_id  not in all_keys:
            c.execute('UPDATE titles SET is_active=0 WHERE id=?', (title_id,))

def clean_bodies(c):
    #c is a db cursor
    all_bodies = []

    json_data = open('topics/topics.json').read()
    topics = json.loads(json_data)
    all_bodies += [body['id'] for topic in topics for body in topic['bodies']]
    
    json_data = open('topics/holidays.json').read()
    topics = json.loads(json_data)
    all_bodies += [body['id'] for topic in topics for body in topic['bodies']]

    json_data = open('topics/special_days.json').read()
    topics = json.loads(json_data)
    all_bodies += [body['id'] for topic in topics for body in topic['bodies']]

    c.execute('SELECT id,body FROM bodies WHERE is_active!=0')
    bodies = c.fetchall()
    for body in bodies:
        if body[1] not in all_bodies:
            c.execute('UPDATE bodies SET is_active=0 WHERE id=?', (body[0],))

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

    c.execute('SELECT id,title,is_active,is_holiday,is_special FROM titles')
    titles = c.fetchall()
    for title in titles:
        print('***************')
        print('id: ' + title[0])
        print('title: ' + title[1])
        
        if not title[2]:
            print('-- INACTIVO --')

        if title[3]:
            c.execute('SELECT day,month FROM holidays WHERE title_id=?',
                (title[0],)
            )
            date = c.fetchone()
            print('-- ¡El '+ str(date[0]) + ' del ' + str(date[1]) +  \
                ' es feriado! --')
        
        if title[4]:
            print('-- Es un día especial. --')

        c.execute('SELECT body,is_active FROM bodies WHERE title_id=?',
            (title[0],)
        )
        bodies = c.fetchall()
        for body in bodies:
            if not body[1]:
                print('-- INACTIVO --')
            print('\t' + body[0])
            if not body[1]:
                print('-- --')
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
