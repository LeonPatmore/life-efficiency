from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from todo.todo_manager import TodoManager, TodoStatus


class TodoHandler(LambdaSplitter):

    def __init__(self, todo_manager: TodoManager):
        super().__init__("subcommand")
        self.todo_manager = todo_manager
        self.add_sub_handler("list", LambdaTarget(self._get_items, response_handler=JsonResponseHandler()))
        self.add_sub_handler("non_completed",
                             LambdaTarget(self._get_non_completed_items, response_handler=JsonResponseHandler()))

    def _get_items(self):
        return [x.to_json() for x in self.todo_manager.get_items()]

    def _get_non_completed_items(self):
        return [x.to_json() for x in filter(lambda item: item.status in [TodoStatus.not_started,
                                                                         TodoStatus.in_progress],
                                            self.todo_manager.get_items())]
