from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from shopping.shopping_lambda_handlers import ShoppingHandler
from todo.todo_lambda_handler import TodoHandler


class LifeEfficiencyLambdaHandler(LambdaSplitter):

    def __init__(self, shopping_handler: ShoppingHandler, todo_handler: TodoHandler):
        super().__init__("command")
        self.add_sub_handler("shopping", LambdaTarget(shopping_handler))
        self.add_sub_handler("todo", LambdaTarget(todo_handler))
