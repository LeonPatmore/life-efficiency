from helpers.datetime import get_current_datetime_utc
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator
from todo.todo_manager import TodoManager, TodoStatus, TodoItem


class TodoHandler(LambdaSplitter):

    def __init__(self, todo_manager: TodoManager):
        super().__init__("subcommand")
        self.todo_manager = todo_manager
        self.add_sub_handler("list", LambdaTarget(self._get_items, response_handler=JsonResponseHandler()))
        self.add_sub_handler("non_completed",
                             LambdaTarget(self._get_non_completed_items, response_handler=JsonResponseHandler()))
        self.add_sub_handler('list', LambdaTarget(self._add_item, [JsonBodyValidator(["desc"])]), 'POST')
        self.add_sub_handler('list', LambdaTarget(self._update_item,
                                                  validators=[JsonBodyValidator(["id", "status"])],
                                                  response_handler=JsonResponseHandler()), 'PATCH')

    def _get_items(self):
        return [x.to_json() for x in self.todo_manager.get_items()]

    def _get_non_completed_items(self):
        return [x.to_json() for x in filter(lambda item: item.status in [TodoStatus.not_started,
                                                                         TodoStatus.in_progress],
                                            self.todo_manager.get_items())]

    def _add_item(self, json):
        self.todo_manager.add_item(TodoItem(json["desc"], TodoStatus.not_started, get_current_datetime_utc()))

    def _update_item(self, json):
        self.todo_manager.update_item(json["id"], getattr(TodoStatus, json["status"]))
        return self.todo_manager.get_item(json["id"]).to_json()
