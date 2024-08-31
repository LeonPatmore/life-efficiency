import numpy
from matplotlib import pyplot
from matplotlib.ticker import FormatStrFormatter

from finance.finance_manager import BalanceRange


class FinanceGraphManager:

    def __init__(self, balance_range: BalanceRange):
        self.balance_range = balance_range

    def _setup_graph(self, func: callable):
        weeks_points = list(self.balance_range.balances.keys())
        fig, axs = pyplot.subplots()
        func(fig, axs, weeks_points)
        axs.yaxis.set_major_formatter(FormatStrFormatter('£%d'))
        axs.set_xticks(weeks_points)
        axs.set_xticklabels(axs.get_xticklabels(), rotation=45)
        axs.set_xlabel("Date")
        axs.set_ylabel("Amount")
        axs.xaxis_date()
        fig.tight_layout()
        return fig

    def generate_balance_summary(self):
        return self._setup_graph(lambda _, axs, weeks_points:
                                 axs.plot(weeks_points, [x.total for x in self.balance_range.balances.values()], 'g'))

    def generate_weekly_difference_summary(self):
        def _(fig, axs, weeks_points):
            axs.axhline(y=0, color='black', linestyle='-')
            increases = [x.total_increase if x.total_increase else numpy.nan for x in self.balance_range.balances.values()]
            total_bar = axs.bar(weeks_points, increases)
            fig.legend((total_bar[0],), ("total",), loc="upper left")
            # for holder in self.balance_range.all_holders:
            #     holder_increases =
        return self._setup_graph(_)
