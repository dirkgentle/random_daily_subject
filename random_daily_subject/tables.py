class Topics:
    name = "Topics"
    key_schema = [{"AttributeName": "id", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "id", "AttributeType": "S"}]


class Submissions:
    name = "Submissions"
    key_schema = [{"AttributeName": "date", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "date", "AttributeType": "S"}]
