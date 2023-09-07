from goals.goals_manager import GoalsManager
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler


class GoalsHandler(LambdaSplitter):

    def __init__(self, goals_manager: GoalsManager):
        super().__init__("subcommand")
        self.goals_manager = goals_manager
        self.add_sub_handler("list", LambdaTarget(goals_manager.get_goals, response_handler=JsonResponseHandler()))
