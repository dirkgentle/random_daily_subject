import db_handler
import datetime
import sqlite3


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
        c.execute('UPDATE titles SET count = count + 1 WHERE id=?',
            (title_id,))
        if body_id:
            c.execute('UPDATE bodies SET count = count + 1 WHERE id=?',
                (body_id,))
    conn.commit()
    c.close()
