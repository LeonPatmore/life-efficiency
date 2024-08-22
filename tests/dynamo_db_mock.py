# noinspection PyPep8Naming
class DynamoDbMock:

    def __init__(self, items=None):
        if items is None:
            items = []
        self.items = items

    def scan(self):
        return {
            "Items": self.items
        }

    def get_item(self, Key: dict):
        matching_items = list(filter(lambda x: x["id"] == Key["id"], self.items))
        if len(matching_items) > 0:
            return {
                "Item": list(filter(lambda x: x["id"] == Key["id"], self.items))[0]
            }
        else:
            return {}

    def put_item(self, Item: dict):
        self.items.append(Item)

    def update_item(self, Key: dict, UpdateExpression: str, ExpressionAttributeValues: dict, **_):
        item = list(filter(lambda x: x["id"] == Key["id"], self.items))[0]
        key = UpdateExpression.split("=")[0][4:]
        item[key] = list(ExpressionAttributeValues.values())[0]

    def delete_item(self, Key: dict):
        item = list(filter(lambda x: x["id"] == Key["id"], self.items))[0]
        self.items.remove(item)
