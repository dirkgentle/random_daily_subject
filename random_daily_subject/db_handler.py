import json
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Body, Holiday, Submission, Title
from config import BasicConfig


class DBHandler:
    def __init__(self):
        self.engine = create_engine(BasicConfig.db_path)

        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def load_topics(self):
        """
        Load all topics from JSON files into the target database.
        """
        for topic_file in BasicConfig.topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)

            is_holiday = topic_file.get("is_holiday", False)
            is_special = topic_file.get("is_special", False)

            for topic in topics:
                now = datetime.now()

                title = (
                    self.session.query(Title).filter_by(id=topic["id"]).one_or_none()
                )
                if title is None:
                    title = Title(
                        id=topic["id"], count=topic.get("count", 0), created_at=now,
                    )

                title.title = topic["title"]
                title.is_holiday = is_holiday
                title.is_special = is_special
                title.modified_at = now
                title.is_active = True

                if is_holiday:
                    holiday = (
                        self.session.query(Holiday)
                        .filter_by(title_id=topic["id"])
                        .one_or_none()
                    )
                    if holiday is None:
                        holiday = Holiday(created_at=now)

                    holiday.day = topic["day"]
                    holiday.month = topic["month"]
                    holiday.modified_at = now
                    holiday.is_active = True

                    title.holidays = [holiday]

                for body in topic.get("bodies"):
                    db_body = (
                        self.session.query(Body).filter_by(id=body["id"]).one_or_none()
                    )
                    if db_body is None:
                        db_body = Body(
                            id=body["id"], count=body.get("count", 0), created_at=now
                        )

                    db_body.body = body["text"]
                    db_body.modified_at = now
                    db_body.is_active = True

                    title.bodies.append(db_body)

                self.session.add(title)
        self.session.commit()

    def clean_topics(self):
        """
        Deactivate topics not present in the topic files.
        """
        active_topics = []
        for topic_file in BasicConfig.topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)
            active_topics += topics

        active_titles = [topic["id"] for topic in active_topics]
        active_bodies = [
            body["id"] for topic in active_topics for body in topic["bodies"]
        ]
        now = datetime.now()

        for db_title in self.session.query(Title).filter_by(is_active=True):
            if db_title.id not in active_titles:
                db_title.is_active = False
                db_title.modified_at = now

        for db_body in self.session.query(Body).filter_by(is_active=True):
            if db_body.id not in active_bodies:
                db_body.is_active = False
                db_body.modified_at = now

        self.session.commit()

    def add_submission(self, title_id, body_id=None, date=None):
        """
        Add a submission to the db.
        """
        if date is None:
            date = datetime.now()

        submission = Submission(date=date, weekday=date.weekday())

        submission.title = self.session.query(Title).filter_by(id=title_id).one()
        submission.title.count += 1
        if body_id is not None:
            submission.body = self.session.query(Body).filter_by(id=body_id).one()
            submission.body.count += 1

        self.session.add(submission)
        self.session.commit()

    def is_date_holiday(self, date):
        """
        Check if a given date is a holiday or not.
        """
        return bool(
            self.session.query(Holiday)
            .filter_by(day=date.day, month=date.month)
            .one_or_none()
        )

    def get_date_holiday(self, date):
        """
        Returns the title object for a given date if it's a holiday
        """
        return (
            self.session.query(Holiday)
            .filter_by(day=date.day, month=date.month)
            .one()
            .title
        )

    def get_all_titles(self):
        """
        Get all available titles.
        """
        return self.session.query(Title).all()

    def get_title(self, title_id):
        """
        Get a title text from its title id.
        """
        return self.session.query(Title).filter_by(id=title_id).one()

    def get_all_bodies(self, title_id):
        """
        Get all available bodies for a specific title.
        """
        return self.session.query(Body).filter_by(title_id=title_id).all()

    def get_body(self, body_id):
        """
        Get a title text from its title id.
        """
        return self.session.query(Body).filter_by(id=body_id).one()

    def get_latest_submissions(self, n=6):
        """
        Return the last `n` submissions from the db.
        """
        return self.session.query(Submission).order_by(Submission.date.asc())[:n]

    def print_topics(self):
        """
        Human readable view of the topics from the db.
        """
        for title in self.session.query(Title):
            print("*" * 15)
            print(f"id: {title.id}")
            print(f"title: {title.title}")

            if not title.is_active:
                print("-- INACTIVE --")
            if title.is_holiday:
                holiday = self.session.query(Holiday).filter_by(title_id=title.id).one()
                print(f"-- Day {holiday.day} of month {holiday.month} is a holiday! --")
            if title.is_special:
                print("-- It's a special day. --")

            for body in title.bodies:
                if not body.is_active:
                    print("-- INACTIVE --")
                print(f"\t {body.body}")
                if not body.is_active:
                    print("-- --")
        print("*" * 15)

    def print_submitted(self):
        """
        Human readable view of the db submissions.
        """
        for submission in self.session.query(Submission):
            print("*" * 15)
            print(f"{submission.date} wday = {submission.weekday}")
            print(f"Title: {submission.title.title}")
            if submission.body:
                print(f"Body: {submission.body.body}")


if __name__ == "__main__":
    db_handler = DBHandler()
    db_handler.load_topics()
    db_handler.clean_topics()
    db_handler.print_topics()
