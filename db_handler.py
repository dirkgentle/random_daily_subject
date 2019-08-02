import datetime
import json
import sqlite3


class DatabaseHandler:
    def __init__(self, db_name):
        self._conn = sqlite3.connect(db_name)
        self._cursor = self._conn.cursor()

    def __del__(self):
        self._conn.commit()
        self._cursor.close()
        self._conn.close()

    def up_db(self):
        self.create_tables_db()
        self.clean_db()
        self.load_topics()

    topic_files = [
        {"path": "topics/topics.json", "is_holiday": 0, "is_special": 0},
        {"path": "topics/holidays.json", "is_holiday": 1, "is_special": 0},
        {"path": "topics/special_days.json", "is_holiday": 0, "is_special": 1},
    ]

    def create_tables_db(self):
        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS titles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            count INTEGER,
            is_holiday INTEGER,
            is_special INTEGER,
            is_active INTEGER,
            created_at TEXT,
            modified_at TEXT
            )"""
        )  # is_xxx == 0 if not xxx, true for other cases
        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS bodies (
            id TEXT PRIMARY KEY,
            body TEXT NOT NULL,
            count INTEGER,
            title_id INTEGER NOT NULL,
            is_active INTEGER,
            created_at TEXT,
            modified_at TEXT,
            FOREIGN KEY(title_id) REFERENCES titles(id)
            )"""
        )
        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS submitted (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            weekday INTEGER,
            title_id TEXT NOT NULL,
            body_id TEXT,
            FOREIGN KEY(title_id) REFERENCES titles(id),
            FOREIGN KEY(body_id) REFERENCES bodies(id)
            )"""
        )
        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS holidays (
            title_id TEXT PRIMARY KEY,
            day INTEGER NOT NULL,
            month INTEGER,
            is_active INTEGER,
            created_at TEXT,
            modified_at TEXT,
            FOREIGN KEY(title_id) REFERENCES titles(id)
            )"""
        )

    def load_topics(self):
        for topic_file in self.topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)

            for topic in topics:
                self.update_title(
                    topic,
                    is_holiday=topic_file["is_holiday"],
                    is_special=topic_file["is_special"],
                )
                if topic_file["is_holiday"]:
                    self.update_holiday(topic)

                for body in topic.get("bodies"):
                    self.update_body(body, topic["id"])

    # update the database section
    def update_title(self, topic, is_holiday=0, is_special=0):
        self._cursor.execute("SELECT is_active FROM titles WHERE id=?", (topic["id"],))
        db_topic = self._cursor.fetchone()
        if not db_topic:
            self._cursor.execute(
                "INSERT INTO titles VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                (
                    topic["id"],
                    topic["title"],
                    topic["count"],
                    is_holiday,
                    is_special,
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                ),
            )
        else:
            self._cursor.execute(
                """UPDATE titles SET
                title=?,is_holiday=?,is_special=?,is_active=1,modified_at=?
                WHERE id=?""",
                (
                    topic["title"],
                    is_holiday,
                    is_special,
                    datetime.datetime.now(),
                    topic["id"],
                ),
            )
        return self._cursor.lastrowid

    def update_body(self, body, title_id):
        self._cursor.execute(
            "SELECT is_active, body FROM bodies WHERE id=?", (body["id"],)
        )
        db_body = self._cursor.fetchone()
        if not db_body:
            self._cursor.execute(
                "INSERT INTO bodies VALUES (?, ?, ?, ?, 1, ?, ?)",
                (
                    body["id"],
                    body["text"],
                    body["count"],
                    title_id,
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                ),
            )
        elif db_body[0] == 0 or db_body[1] != body["text"]:
            self._cursor.execute(
                """UPDATE bodies SET
                body=?,title_id=?,is_active=1,modified_at=? WHERE id=?""",
                (body["text"], title_id, datetime.datetime.now(), body["id"]),
            )

    def update_submitted(self, title_id, body_id=None):
        self._cursor.execute(
            "INSERT INTO submitted VALUES (NULL, ?, ?, ?, ?)",
            (
                datetime.datetime.now(),
                datetime.date.today().weekday(),
                title_id,
                body_id,
            ),
        )
        self._cursor.execute(
            "UPDATE titles SET count = count + 1 WHERE id=?", (title_id,)
        )
        if body_id:
            self._cursor.execute(
                "UPDATE bodies SET count = count + 1 WHERE id=?", (body_id,)
            )

    def update_holiday(self, topic):
        self._cursor.execute("SELECT * FROM holidays WHERE title_id=?", (topic["id"],))
        db_topic = self._cursor.fetchone()
        if not db_topic:
            self._cursor.execute(
                "INSERT INTO holidays VALUES (?, ?, ?, 1, ?, ?)",
                (
                    topic["id"],
                    topic["day"],
                    topic["month"],
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                ),
            )
        else:
            self._cursor.execute(
                """UPDATE holidays SET day=?,month=?,is_active=1,modified_at=?
                WHERE title_id=?""",
                (topic["day"], topic["month"], datetime.datetime.now(), topic["id"]),
            )

    # db reading section
    def is_date_holiday(self, date):
        self._cursor.execute(
            "SELECT title_id FROM holidays WHERE (day,month)=(?,?)",
            (date.day, date.month),
        )
        return self._cursor.fetchone()

    def is_today_holiday(self):
        return self.is_date_holiday(datetime.datetime.today())

    def get_latest_submissions(self, n=6):
        self._cursor.execute(
            "SELECT title_id FROM submitted " "ORDER BY DATETIME(date) DESC LIMIT ?",
            (str(n),),
        )
        return [x[0] for x in self._cursor.fetchall()]

    def get_title(self, title_id):
        self._cursor.execute("SELECT title FROM titles WHERE id=?", (title_id,))
        return self._cursor.fetchone()

    def get_title_id(self, title):
        self._cursor.execute("SELECT id FROM titles WHERE title LIKE ?", (title,))
        return self._cursor.fetchone()

    def get_random_submission(self):
        title_id, title = self.get_random_title()
        body_id, body = self.get_random_body(title_id)
        return (title_id, title, body_id, body)

    def get_random_title(self):
        self._cursor.execute(
            "SELECT id, title FROM titles "
            "WHERE is_holiday = 0 AND is_special = 0 AND is_active != 0 "
            "ORDER BY RANDOM() LIMIT 1"
        )
        return self._cursor.fetchone()

    def get_body(self, body_id):
        self._cursor.execute("SELECT body FROM bodies WHERE id=?", (body_id,))
        return self._cursor.fetchone()

    def get_random_body(self, title_id):
        self._cursor.execute(
            """SELECT id, body FROM bodies
                WHERE title_id = ? AND is_active != 0
                ORDER BY RANDOM() LIMIT 1""",
            (str(title_id),),
        )
        return self._cursor.fetchone()

    def get_all_titles(self, get_counts=False):
        """
        Returns all active titles for normal days.
        """
        sql_cmd = (
            "SELECT id{} FROM titles WHERE "
            "is_active!=0 AND is_holiday==0 AND is_special==0"
        ).format(",count" if get_counts else "")

        self._cursor.execute(sql_cmd)
        return self._cursor.fetchall()

    def get_all_bodies(self, title_id, get_counts=False):
        """
        Returns all active bodies for a given title_id
        """
        sql_cmd = (
            "SELECT id{} FROM bodies WHERE " "is_active!=0 AND title_id=?"
        ).format(",count" if get_counts else "")

        self._cursor.execute(sql_cmd, (title_id,))
        return self._cursor.fetchall()

    # db cleaning section
    def clean_db(self):
        self.clean_titles()
        self.clean_bodies()

    def clean_titles(self):
        all_keys = []

        for topic_file in self.topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)
            all_keys += [topic["id"] for topic in topics]

        self._cursor.execute("SELECT id FROM titles WHERE is_active!=0")
        title_ids = self._cursor.fetchall()
        for title_id in title_ids:
            if title_id not in all_keys:
                self._cursor.execute(
                    "UPDATE titles SET is_active=0 WHERE id=?", (title_id,)
                )

    def clean_bodies(self):
        all_bodies = []

        for topic_file in self.topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)
            all_bodies += [body["id"] for topic in topics for body in topic["bodies"]]

        self._cursor.execute("SELECT id,body FROM bodies WHERE is_active!=0")
        bodies = self._cursor.fetchall()
        for body in bodies:
            if body[1] not in all_bodies:
                self._cursor.execute(
                    "UPDATE bodies SET is_active=0 WHERE id=?", (body[0],)
                )

    # printing data section
    def _print_tables(self, table_name):
        self._cursor.execute(
            "SELECT * FROM {}".format(table_name)
        )  # insecure!!! debug only
        return self._cursor.fetchall()

    def print_topics(self):
        self._cursor.execute(
            "SELECT id,title,is_active,is_holiday,is_special FROM titles"
        )
        titles = self._cursor.fetchall()
        for title in titles:
            print("***************")
            print("id: {}".format(title[0]))
            print("title: {}".format(title[1]))

            if not title[2]:
                print("-- INACTIVO --")

            if title[3]:
                self._cursor.execute(
                    "SELECT day,month FROM holidays WHERE title_id=?", (title[0],)
                )
                date = self._cursor.fetchone()
                print(
                    "-- ¡El "
                    + str(date[0])
                    + " del "
                    + str(date[1])
                    + " es feriado! --"
                )

            if title[4]:
                print("-- Es un día especial. --")

            self._cursor.execute(
                "SELECT body,is_active FROM bodies WHERE title_id=?", (title[0],)
            )
            bodies = self._cursor.fetchall()
            for body in bodies:
                if not body[1]:
                    print("-- INACTIVO --")
                print("\t" + body[0])
                if not body[1]:
                    print("-- --")
        print("***************")

    def print_submitted(self):
        self._cursor.execute("SELECT * from submitted")
        submitted = self._cursor.fetchall()
        for submission in submitted:
            print("***************")
            print(str(submission[1]) + " wday = " + str(submission[2]))
            self._cursor.execute(
                "SELECT title FROM titles WHERE id=?", (submission[3],)
            )
            print(self._cursor.fetchone()[0])
            if submission[4]:
                self._cursor.execute(
                    "SELECT body FROM bodies WHERE id=?", (submission[4],)
                )
                print(self._cursor.fetchone()[0])
        print("***************")
