from datetime import datetime, timedelta

from matplotlib import pyplot
from matplotlib.ticker import FormatStrFormatter

from finance.finance_manager import FinanceManager


class FinanceGraphManager:

    def __init__(self, finance_manager: FinanceManager):
        self.finance_manager = finance_manager

    def generate_weekly_graph(self, start_date: datetime, end_date: datetime, step: timedelta):
        balance_range = self.finance_manager.generate_balances(start_date, end_date, step)
        weeks_points = list(balance_range.balances.keys())
        total_points = [x.total for x in balance_range.balances.values()]

        fig, axs = pyplot.subplots()
        axs.plot_date(weeks_points, total_points, 'g')

        axs.set_xlabel("Date")
        axs.set_ylabel("Amount")
        axs.yaxis.set_major_formatter(FormatStrFormatter('£%d'))
        axs.set_xticks(weeks_points)
        axs.set_xticklabels(axs.get_xticklabels(), rotation=45)
        fig.tight_layout()
        fig.savefig("test-image")
