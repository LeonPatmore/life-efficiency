from datetime import datetime

from finance.balance_change_manager import ChangeReason, BalanceChange
from finance.balance_instance_manager import BalanceInstance
from finance.finance_manager import FinanceManager
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, TypedField, QueryParamValidator


class FinanceHandler(LambdaSplitter):

    def __init__(self, finance_manager: FinanceManager):
        super().__init__("subcommand")
        self.add_sub_handler("instances", LambdaTarget(
            handler=lambda fields: finance_manager.balance_instance_manager.get_all_with_filters(fields["holder"],
                                                                                                 fields["date"]),
            response_handler=JsonResponseHandler(),
            validators=[QueryParamValidator(optional_fields=["holder", TypedField("date", datetime)])]))
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
        self.add_sub_handler("changes", LambdaTarget(
            handler=lambda fields: finance_manager.balance_change_manager.add(
                BalanceChange(fields["reason"], fields["amount"], fields["date"], fields["desc"])),
            response_handler=JsonResponseHandler(),
            validators=[JsonBodyValidator(required_fields=[TypedField("amount", float),
                                                           TypedField("reason", ChangeReason),
                                                           "desc"],
                                          optional_fields=[TypedField("date", datetime)])]),
                             method="POST")
        self.add_sub_handler("range", LambdaTarget(
            handler=lambda fields: finance_manager.generate_balance_range(start_date=fields["start_date"],
                                                                          end_date=fields["end_date"]),
            response_handler=JsonResponseHandler(),
            validators=[QueryParamValidator(required_fields=[TypedField("start_date", datetime)],
                                            optional_fields=[TypedField("end_date", datetime)])]))
