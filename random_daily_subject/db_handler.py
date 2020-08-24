import json
from datetime import datetime
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from .config import BasicConfig, TopicFile
from .tables import Topics, Submissions


class DBHandler:
    def __init__(self, db_url: str = BasicConfig.db_url) -> None:
        self.dynamodb = boto3.resource("dynamodb", endpoint_url=BasicConfig.db_url)

        tables = [Topics, Submissions]
        existing_tables = [table.name for table in self.dynamodb.tables.all()]

        for table in tables:
            if table.name not in existing_tables:
                self.dynamodb.create_table(
                    TableName=table.name,
                    KeySchema=table.key_schema,
                    AttributeDefinitions=table.attribute_definitions,
                    ProvisionedThroughput={
                        "ReadCapacityUnits": 10,
                        "WriteCapacityUnits": 10,
                    },
                )

        self.topics_table = self.dynamodb.Table(Topics.name)
        self.submissions_table = self.dynamodb.Table(Submissions.name)

    def load_topics(
        self, topic_files: List[TopicFile] = BasicConfig.topic_files
    ) -> None:
        """
        Load all topics from JSON files into the target database.
        """
        for topic_file in topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)

            is_holiday = topic_file.get("is_holiday", False)
            is_special = topic_file.get("is_special", False)

            for topic in topics:
                now = datetime.now()

                topic["is_holiday"] = is_holiday
                topic["is_special"] = is_special
                topic["modified_at"] = now.isoformat()
                topic["is_active"] = topic.get("is_active", True)
                topic["count"] = topic.get("count", 0)

                for body in topic["bodies"]:
                    body["modified_at"] = now.isoformat()
                    body["is_active"] = body.get("is_active", True)
                    body["count"] = body.get("count", 0)

                _ = self.topics_table.put_item(Item=topic)

    def clean_topics(
        self, topic_files: List[TopicFile] = BasicConfig.topic_files
    ) -> None:
        """
        Deactivate topics not present in the topic files.
        """
        active_topics = []
        for topic_file in topic_files:
            with open(topic_file["path"]) as f:
                topics = json.load(f)
            active_topics += topics

        active_titles = [topic["id"] for topic in active_topics]
        active_bodies = [
            body["id"] for topic in active_topics for body in topic["bodies"]
        ]
        now = datetime.now().isoformat()

        scan_kwargs = {}

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.topics_table.scan(**scan_kwargs)

            for topic in response.get("Items", []):
                if topic["id"] not in active_titles:
                    response = self.topics_table.update_item(
                        Key={"id": topic["id"]},
                        UpdateExpression="set is_active=:a, modified_at=:n",
                        ExpressionAttributeValues={":a": False, ":n": now},
                        ReturnValues="UPDATED_NEW",
                    )

                bodies_to_update = [
                    body["is_active"] and body not in active_bodies
                    for body in topic["bodies"]
                ]
                if bodies_to_update:
                    for body in topic["bodies"]:
                        if body["id"] not in active_bodies:
                            body["is_active"] = False

                    _ = self.topics_table.update_item(
                        Key={"id": topic["id"]},
                        UpdateExpression="set bodies=:b, modified_at=:n",
                        ExpressionAttributeValues={":b": topic["bodies"], ":n": now},
                        ReturnValues="UPDATED_NEW",
                    )

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

    def add_submission(
        self,
        title_id: str,
        body_id: Optional[str] = None,
        sub_date: Optional[datetime] = None,
    ) -> None:
        """
        Add a submission to the db.
        """
        if sub_date is None:
            sub_date = datetime.now()

        self.submissions_table.put_item(
            Item={
                "date": sub_date.isoformat(),
                "weekday": sub_date.weekday(),
                "title_id": title_id,
                "body_id": body_id,
            }
        )

        topic = self.topics_table.get_item(Key={"id": title_id})["Item"]
        topic["count"] += 1

        if body_id is not None:
            for body in topic["bodies"]:
                if body["id"] == body_id:
                    body["count"] += 1
                    break

        _ = self.topics_table.update_item(
            Key={"id": title_id},
            UpdateExpression="set #c=:c, bodies=:b",
            ExpressionAttributeValues={":c": topic["count"], ":b": topic["bodies"]},
            ExpressionAttributeNames={"#c": "count"},
            ReturnValues="UPDATED_NEW",
        )

    def is_date_holiday(self, date: datetime) -> bool:
        """
        Check if a given date is a holiday or not.
        """
        scan_kwargs = {
            "FilterExpression": Key("day").eq(date.day)
            & Key("month").eq(date.month)
            & Key("is_active").eq(True),
            "ProjectionExpression": "id",
        }

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.topics_table.scan(**scan_kwargs)

            if response.get("Items"):
                return True

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        return False

    def get_date_holiday(self, date: datetime):
        """
        Returns the title object for a given date if it's a holiday
        """
        scan_kwargs = {
            "FilterExpression": Key("day").eq(date.day)
            & Key("month").eq(date.month)
            & Key("is_active").eq(True),
        }

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.topics_table.scan(**scan_kwargs)

            if response.get("Items"):
                return response.get("Items")[0]

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

    def get_all_titles(self):
        """
        Get all available titles that are not holidays or special days.
        """
        scan_kwargs = {
            "FilterExpression": Key("is_active").eq(True)
            & Key("is_holiday").eq(False)
            & Key("is_special").eq(False),
        }
        all_titles = []

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.topics_table.scan(**scan_kwargs)

            all_titles += response.get("Items")

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        return all_titles

    def get_title(self, title_id: str):
        """
        Get a title from its title id.
        """
        response = self.topics_table.get_item(Key={"id": title_id})
        return response.get("Item")

    def get_all_bodies(self, title_id: str):
        """
        Get all available bodies for a specific title.
        """
        response = self.topics_table.get_item(Key={"id": title_id})

        topic = response.get("Item")

        if topic is not None:
            return topic["bodies"]

    def get_body(self, title_id: str, body_id: str):
        """
        Get a title text from its title id.
        """
        response = self.topics_table.get_item(Key={"id": title_id})
        topic = response.get("Item")

        if topic is not None:
            for body in topic["bodies"]:
                if body["id"] == body_id:
                    return body

    def get_latest_submissions(self, n: int = 6):
        """
        Return the last `n` submissions from the db.
        """
        scan_kwargs = {}
        submissions = []

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.submissions_table.scan(**scan_kwargs)

            submissions += response.get("Items")

            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        submissions.sort(key=lambda submission: submission["date"], reverse=True)

        return submissions[:n]

    def print_topics(self) -> None:
        """
        Human readable view of the topics from the db.
        """
        for title in self.get_all_titles():
            print("*" * 15)
            print(f"id: {title['id']}")
            print(f"title: {title['title']}")

            if not title["is_active"]:
                print("-- INACTIVE --")
            if title["is_holiday"]:
                print(
                    f"-- Day {title['day']} of month {title['month']} is a holiday! --"
                )
            if title["is_special"]:
                print("-- It's a special day. --")

            for body in title["bodies"]:
                if not body["is_active"]:
                    print("-- INACTIVE --")
                print(f"\t {body['text']}")
                if not body["is_active"]:
                    print("-- --")
        print("*" * 15)

    def print_submitted(self) -> None:
        """
        Human readable view of the db submissions.
        """
        for submission in self.get_latest_submissions():
            print("*" * 15)
            print(f"{submission['date']} wday = {submission['weekday']}")
            title = self.get_title(submission["title_id"])
            print(f"Title: {title['title']}")
            if submission["body_id"]:
                body = self.get_body(submission["title_id"], submission["body_id"])
                print(f"Body: {body['text']}")


if __name__ == "__main__":
    db_handler = DBHandler()
    db_handler.load_topics()
    db_handler.clean_topics()
    db_handler.print_topics()
