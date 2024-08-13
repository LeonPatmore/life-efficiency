import logging

from helpers.datetime import get_current_datetime_utc
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, QueryParamValidator
from todo.list.todo_list_manager import TodoListManager, TodoStatus, TodoItem
from todo.weekly.todo_weekly_manager import TodoWeeklyManager


class TodoHandler(LambdaSplitter):

    def __init__(self, todo_list_manager: TodoListManager, todo_weekly_manager: TodoWeeklyManager):
        super().__init__("subcommand")
        self.todo_list_manager = todo_list_manager
        self.todo_weekly_manager = todo_weekly_manager
        self.add_sub_handler("list", LambdaTarget(self._get_todo_list, response_handler=JsonResponseHandler()))
        self.add_sub_handler("non_completed",
                             LambdaTarget(self._get_non_completed_items, response_handler=JsonResponseHandler()))
        self.add_sub_handler('list', LambdaTarget(self._add_item,
                                                  [JsonBodyValidator(["desc"])],
                                                  JsonResponseHandler()), 'POST')
        self.add_sub_handler('list', LambdaTarget(self._update_item,
                                                  validators=[JsonBodyValidator(["id", "status"])],
                                                  response_handler=JsonResponseHandler()), 'PATCH')
        self.add_sub_handler("list", LambdaTarget(self._remove_item), method="DELETE")
        self.add_sub_handler("weekly", LambdaTarget(self._get_weekly_items,
                                                    validators=[QueryParamValidator(["day"])],
                                                    response_handler=JsonResponseHandler()))
        self.add_sub_handler("weekly", LambdaTarget(self._get_weekly_items, response_handler=JsonResponseHandler()))
        self.add_sub_handler("weekly",
                             LambdaTarget(self._complete_weekly_item, validators=[QueryParamValidator(["id"])]),
                             "POST")

    def _get_weekly_items(self, params):
        if "day" in params:
            logging.info(f"Looking up weekly items for day [ {params['day']} ]")
            return [x.to_json() for x in self.todo_weekly_manager.get_todo_for_day(int(params["day"]))]
        else:
            logging.info("Looking up all weekly items")
            return [x.to_json() for x in self.todo_weekly_manager.get_ordered_todos()]

    def _complete_weekly_item(self, params):
        self.todo_weekly_manager.complete_todo_for_item(params["id"])

    def _get_todo_list(self, params):
        items = self.todo_list_manager.get_items()
        if params is not None and "status" in params:
            items = list(filter(lambda x: x.status.name == params["status"], items))
        if params is not None and "sort" in params and params["sort"]:
            items.sort(key=lambda x: x.date_added.timestamp(), reverse=True)
        return [x.to_json() for x in items]

    def _get_non_completed_items(self):
        return [x.to_json() for x in filter(lambda item: item.status in [TodoStatus.not_started,
                                                                         TodoStatus.in_progress],
                                            self.todo_list_manager.get_items())]

    def _add_item(self, json) -> TodoItem:
        return self.todo_list_manager.add_item(TodoItem(json["desc"], TodoStatus.not_started, get_current_datetime_utc()))

    def _update_item(self, json):
        self.todo_list_manager.update_item(json["id"], getattr(TodoStatus, json["status"]))
        return self.todo_list_manager.get_item(json["id"]).to_json()

    def _remove_item(self, path: str):
        item_id = path.split("/")[-1]
        self.todo_list_manager.remove_item(item_id)
