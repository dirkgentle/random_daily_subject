import datetime
import sqlite3

from random_daily_subject.db_handler import DBHandler
from random_daily_subject.config import BasicConfig


# update db when the topics are updated
def update_bot_db():
    database = DBHandler(BasicConfig.db_path)
    database.load_topics()
    database.clean_topics()
    database.print_topics()


# set up database for use with the bot
def set_up_bot():
    # bot comments every day at 8:02 AM
    bot_time_hours = 8
    bot_time_minutes = 2
    already_posted = (
        bot_time_hours < datetime.datetime.now().hour
        or bot_time_hours == datetime.datetime.now().hour
        and bot_time_minutes < datetime.datetime.now().minute
    )

    _ = DBHandler(BasicConfig.db_path)
    migrate_log_to_db("log.txt", BasicConfig.db_path, already_posted)


def add_debug_columns():
    db_name = "topics.db"
    now = datetime.datetime.now()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("ALTER TABLE titles ADD COLUMN 'created_at' 'TEXT'")
    c.execute("ALTER TABLE titles ADD COLUMN 'modified_at' 'TEXT'")
    c.execute("UPDATE titles SET created_at=?,modified_at=?", (now, now))

    c.execute("ALTER TABLE bodies ADD COLUMN 'created_at' 'TEXT'")
    c.execute("ALTER TABLE bodies ADD COLUMN 'modified_at' 'TEXT'")
    c.execute("UPDATE bodies SET created_at=?,modified_at=?", (now, now))

    c.execute("ALTER TABLE holidays ADD COLUMN 'is_active' 'INTEGER'")
    c.execute("ALTER TABLE holidays ADD COLUMN 'created_at' 'TEXT'")
    c.execute("ALTER TABLE holidays ADD COLUMN 'modified_at' 'TEXT'")
    c.execute(
        "UPDATE holidays SET is_active=?,created_at=?,modified_at=?", (1, now, now)
    )

    conn.commit()
    c.close()


# Para migrar los datos viejos
def migrate_log_to_db(log_path, db_name, already_posted_today):
    with open(log_path) as old_log:
        log = [x.strip("\n") for x in old_log.readlines()]
    log = reversed(log)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    for i, topic in enumerate(log):
        print(topic)
        c.execute("SELECT id FROM titles WHERE title=?", (topic,))
        title_id = c.fetchone()[0]
        c.execute("SELECT id FROM bodies WHERE title_id=?", (title_id,))
        body_id = c.fetchall()[0][0]

        if already_posted_today:
            topic_date = datetime.date.today() - datetime.timedelta(days=i)
        else:
            topic_date = datetime.date.today() - datetime.timedelta(days=i + 1)
        topic_weekday = topic_date.weekday()

        c.execute(
            "INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)",
            (topic_date, topic_weekday, title_id, body_id),
        )
        c.execute("UPDATE titles SET count = count + 1 WHERE id=?", (title_id,))
        if body_id:
            c.execute("UPDATE bodies SET count = count + 1 WHERE id=?", (body_id,))
    conn.commit()
    c.close()


def fix_submitted_primary_key():
    """
    In an older version all submissions had NULL as their primary key.
    """
    conn = sqlite3.connect("../db/topics.db")
    c = conn.cursor()

    old_rows = c.execute("SELECT * FROM submitted").fetchall()

    c.execute("DROP TABLE submitted")
    c.execute(
        """CREATE TABLE IF NOT EXISTS submitted (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        weekday INTEGER,
        title_id TEXT NOT NULL,
        body_id TEXT,
        FOREIGN KEY(title_id) REFERENCES titles(id),
        FOREIGN KEY(body_id) REFERENCES bodies(id)
        )"""
    )

    for idx, (id, date, weekday, title_id, body_id) in enumerate(old_rows, 1):
        c.execute(
            "INSERT INTO submitted VALUES (?, ?, ?, ?, ?)",
            (idx, date, weekday, title_id, body_id),
        )

    conn.commit()
    c.close()


def fix_submitted_date():
    """
    Older submissions have dates instead of datetime.
    """
    conn = sqlite3.connect("../db/topics.db")
    c = conn.cursor()

    old_rows = c.execute("SELECT id, date FROM submitted").fetchall()
    for id, date in old_rows:
        if ":" not in date:
            parsed = str(datetime.datetime.strptime(date, "%Y-%m-%d"))
            c.execute("UPDATE submitted SET date=? WHERE id=?", (parsed, id))

    conn.commit()
    c.close()
