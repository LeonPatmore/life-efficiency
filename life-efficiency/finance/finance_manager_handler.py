from finance.finance_manager import BalanceInstanceManager, BalanceInstance
from helpers.datetime import string_to_datetime
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler


class FinanceHandler(LambdaSplitter):

    def __init__(self, balance_instance: BalanceInstanceManager):
        super().__init__("subcommand")
        self.add_sub_handler("instances", LambdaTarget(balance_instance.get_instances,
                                                       response_handler=JsonResponseHandler()),
                             method="GET")
        self.add_sub_handler("instances", LambdaTarget(
            handler=lambda json: balance_instance.add_instance(BalanceInstance(amount=json["amount"],
                                                                               holder=json["holder"],
                                                                               date=string_to_datetime(json["date"]))),
            response_handler=JsonResponseHandler()),
                             method="POST")
