from datetime import datetime

from finance.finance_manager import BalanceInstance, FinanceManager
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, TypedField


class FinanceHandler(LambdaSplitter):

    def __init__(self, finance_manager: FinanceManager):
        super().__init__("subcommand")
        self.add_sub_handler("instances", LambdaTarget(finance_manager.balance_instance_manager.get_all,
                                                       response_handler=JsonResponseHandler()))
        self.add_sub_handler("instances", LambdaTarget(
            handler=lambda fields: finance_manager.balance_instance_manager.add(BalanceInstance(amount=fields["amount"],
                                                                                                holder=fields["holder"],
                                                                                                date=fields["date"])),
            response_handler=JsonResponseHandler(),
            validators=[JsonBodyValidator(required_fields=[TypedField("amount", float), "holder"],
                                          optional_fields=[TypedField("date", datetime)])]),
                             method="POST")
        self.add_sub_handler("changes",
                             LambdaTarget(handler=finance_manager.balance_change_manager.get_all,
                                          response_handler=JsonResponseHandler()))
