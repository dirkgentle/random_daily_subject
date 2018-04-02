import sqlite3
import datetime


def create_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE submitted 
        (key INTEGER PRIMARY KEY, date TEXT, weekday INTEGER, title TEXT)''')

    conn.commit()
    c.close()

#it asumes that the bot has already run today
def migrate_log_to_db(log_path, db_name):
    with open(log_path) as old_log:
        log = [x.strip('\n') for x in old_log.readlines()]
    log = reversed(log)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    for i, topic in enumerate(log):
        print(topic)
        topic_date = (datetime.date.today() - datetime.timedelta(days=i))
        topic_weekday = topic_date.weekday()
        print((datetime.date.today() - datetime.timedelta(days=i)))
        c.execute('INSERT INTO submitted VALUES (NULL, ?, ?, ?)',
            (topic_date, topic_weekday, topic))

    conn.commit()
    c.close()
