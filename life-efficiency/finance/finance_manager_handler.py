from datetime import datetime

from finance.finance_manager import BalanceInstanceManager, BalanceInstance
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, TypedField


class FinanceHandler(LambdaSplitter):

    def __init__(self, balance_instance: BalanceInstanceManager):
        super().__init__("subcommand")
        self.add_sub_handler("instances", LambdaTarget(balance_instance.get_all,
                                                       response_handler=JsonResponseHandler()),
                             method="GET")
        self.add_sub_handler("instances", LambdaTarget(
            handler=lambda fields: balance_instance.add(BalanceInstance(amount=fields["amount"],
                                                                        holder=fields["holder"],
                                                                        date=fields["date"])),
            response_handler=JsonResponseHandler(),
            validators=[JsonBodyValidator(required_fields=[TypedField("amount", float), "holder"],
                                          optional_fields=[TypedField("date", datetime)])]),
                             method="POST")
