from helpers.datetime import string_to_datetime, datetime_to_string
from todo.list.todo_list_manager import TodoListManager, TodoItem, TodoStatus


class TodoListManagerDynamo(TodoListManager):

    def __init__(self, table, current_time_provider: callable):
        self.table = table
        self.current_time_provider = current_time_provider

    @staticmethod
    def _convert_item_to_dto(x) -> TodoItem:
        return TodoItem(x["Desc"],
                        getattr(TodoStatus, x["Status"]),
                        string_to_datetime(x["DateAdded"]),
                        item_number=int(x["Id"]),
                        date_done=string_to_datetime(x["DateDone"] if "DateDone" in x else None))

    def get_items(self) -> list[TodoItem]:
        return [self._convert_item_to_dto(x) for x in self.table.scan()["Items"]]

    def add_item(self, item: TodoItem):
        if item.item_number is not None:
            item_number = item.item_number
        else:
            item_number = len(self.get_items()) + 1
        self.table.put_item(Item={"Id": int(item_number),
                                  "Status": item.status.name,
                                  "DateAdded": datetime_to_string(item.date_added),
                                  "DateDone": datetime_to_string(item.date_done) if item.date_done else "",
                                  "Desc": item.desc})

    def get_item(self, item_id: int) -> TodoItem:
        return self._convert_item_to_dto(self.table.get_item(Key={'Id': item_id}))

    def update_item(self, item_id: int, status: TodoStatus):
        self.table.update_item(Key={"Id": item_id},
                               UpdateExpression="set Status=:s",
                               ExpressionAttributeValues={":s": status.name})
        if status == TodoStatus.done:
            current_time = datetime_to_string(self.current_time_provider())
            self.table.update_item(Key={"Id": item_id},
                                   UpdateExpression="set DateDone=:d",
                                   ExpressionAttributeValues={":d": current_time})
