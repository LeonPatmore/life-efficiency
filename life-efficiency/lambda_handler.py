from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from todo.todo_manager import TodoManager


class LifeEfficiencyLambdaHandler(LambdaSplitter):

    def __init__(self, shopping_handler: LambdaSplitter, todo_manager: TodoManager):
        super().__init__("command")
        self.add_sub_handler("shopping", LambdaTarget(shopping_handler))
        self.add_sub_handler("todo", LambdaTarget(lambda: todo_manager.get_items()))
