from finance.finance_manager_handler import FinanceHandler
from goals.goals_lambda_handler import GoalsHandler
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget, ANY_METHOD
from shopping.shopping_lambda_handlers import ShoppingHandler
from todo.todo_lambda_handler import TodoHandler


class LifeEfficiencyLambdaHandler(LambdaSplitter):

    def __init__(self,
                 shopping_handler: ShoppingHandler,
                 todo_handler: TodoHandler,
                 goals_handler: GoalsHandler,
                 finance_handler: FinanceHandler):
        super().__init__("command")
        self.add_sub_handler("shopping", LambdaTarget(shopping_handler), method=ANY_METHOD)
        self.add_sub_handler("todo", LambdaTarget(todo_handler), method=ANY_METHOD)
        self.add_sub_handler("goals", LambdaTarget(goals_handler), method=ANY_METHOD)
        self.add_sub_handler("finance", LambdaTarget(finance_handler), method=ANY_METHOD)
