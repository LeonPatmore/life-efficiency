import logging
import uuid

from helpers.datetime import string_to_datetime, datetime_to_string
from todo.list.todo_list_manager import TodoListManager, TodoItem, TodoStatus


class TodoListManagerDynamo(TodoListManager):

    def __init__(self, table, current_time_provider: callable):
        self.table = table
        self.current_time_provider = current_time_provider

    @staticmethod
    def _convert_item_to_dto(x) -> TodoItem:
        return TodoItem(x["Desc"],
                        TodoStatus[x["TodoStatus"]],
                        string_to_datetime(x["DateAdded"]),
                        item_id=x["id"],
                        date_done=string_to_datetime(x["DateDone"]) if "DateDone" in x and x["DateDone"] else None)

    def get_items(self) -> list[TodoItem]:
        return [self._convert_item_to_dto(x) for x in self.table.scan()["Items"]]

    def add_item(self, item: TodoItem) -> TodoItem:
        if item.item_id is not None:
            item_id = item.item_id
        else:
            item_id = str(uuid.uuid4())
        logging.info(f"Creating item with id {item_id}")
        self.table.put_item(Item={"id": item_id,
                                  "TodoStatus": item.status.name,
                                  "DateAdded": datetime_to_string(item.date_added),
                                  "DateDone": datetime_to_string(item.date_done) if item.date_done else "",
                                  "Desc": item.desc})
        return self.get_item(item_id)

    def get_item(self, item_id: str) -> TodoItem:
        return self._convert_item_to_dto(self.table.get_item(Key={'id': str(item_id)})["Item"])

    def update_item(self, item_id: str, status: TodoStatus):
        logging.info(f"Updating item {item_id} with status {status.name}")
        self.table.update_item(Key={"id": item_id},
                               ConditionExpression='attribute_exists(id)',
                               UpdateExpression="set TodoStatus=:s",
                               ExpressionAttributeValues={":s": status.name})
        if status == TodoStatus.done:
            current_time = datetime_to_string(self.current_time_provider())
            self.table.update_item(Key={"id": item_id},
                                   ConditionExpression='attribute_exists(id)',
                                   UpdateExpression="set DateDone=:d",
                                   ExpressionAttributeValues={":d": current_time})

    def remove_item(self, item_id: str):
        self.table.delete_item(Key={"id": item_id})
