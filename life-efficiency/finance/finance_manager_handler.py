import io
import uuid
from dataclasses import dataclass
from datetime import datetime

from matplotlib.figure import Figure

from finance.balance_change_manager import ChangeReason, BalanceChange
from finance.balance_instance_manager import BalanceInstance
from finance.finance_manager import FinanceManager
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, TypedField, QueryParamValidator
from uploader.uploader import UploaderService

RANGE_VALIDATOR = QueryParamValidator(required_fields=[TypedField("start_date", datetime)],
                                      optional_fields=[TypedField("end_date", datetime)])


@dataclass
class FigureLink:
    link: str


class FinanceGraphHandler(LambdaSplitter):

    def __init__(self, finance_manager: FinanceManager, file_uploader: UploaderService):
        super().__init__("subcommand", 1)
        self.file_uploader = file_uploader
        self.add_sub_handler("weekly-difference", LambdaTarget(
            handler=lambda fields: self.figure_to_link(finance_manager.generate_graph_manager(
                finance_manager.generate_balance_range(start_date=fields["start_date"], end_date=fields["end_date"])
            ).generate_weekly_difference_summary()),
            validators=[RANGE_VALIDATOR],
            response_handler=JsonResponseHandler()
        ))

    def figure_to_link(self, fig: Figure) -> FigureLink:
        fig_bytes = self.figure_to_bytes(fig)
        figure_id = str(uuid.uuid4())
        link = self.file_uploader.upload(f"figure-{figure_id}", fig_bytes, "image/png")
        return FigureLink(link)

    @staticmethod
    def figure_to_bytes(fig: Figure) -> io.BytesIO:
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return buf


class FinanceHandler(LambdaSplitter):

    def __init__(self, finance_manager: FinanceManager, graph_handler: FinanceGraphHandler):
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
            validators=[RANGE_VALIDATOR]))
        self.add_sub_handler("graph", LambdaTarget(graph_handler))
        self.add_sub_handler("metadata", LambdaTarget(
            handler=finance_manager.metadata_loader.get_metadata,
            response_handler=JsonResponseHandler()))
