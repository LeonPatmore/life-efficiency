import numpy
from matplotlib import pyplot
from matplotlib.ticker import FormatStrFormatter

from finance.finance_domain import BalanceRange
from finance.metadata.finance_metadata import FinanceMetadata


class FinanceGraphManager:

    def __init__(self, balance_range: BalanceRange, metadata: FinanceMetadata):
        self.balance_range = balance_range
        self.metadata = metadata

    def _setup_graph(self, func: callable):
        weeks_points = list(self.balance_range.balances.keys())
        ind = numpy.arange(len(weeks_points))
        fig, axs = pyplot.subplots()
        func(fig, axs, ind)
        axs.yaxis.set_major_formatter(FormatStrFormatter('£%d'))
        axs.set_xticks(ind, weeks_points)
        axs.set_xticklabels(axs.get_xticklabels(), rotation=45)
        axs.set_xlabel("Date")
        axs.set_ylabel("Amount")
        fig.tight_layout()
        return fig

    def generate_balance_summary(self):
        return self._setup_graph(lambda _, axs, weeks_points:
                                 axs.plot(weeks_points, [x.total for x in self.balance_range.balances.values()], 'g'))

    def generate_weekly_difference_summary(self):
        def _(fig, axs, ind):
            take_home = self.metadata.get_take_home_for_timedelta(self.balance_range.step)
            axs.axhline(y=0, color='black', linestyle='-')
            axs.axhline(y=-take_home, color='red', linestyle='-')
            increases = [x.total_increase if x.total_increase else numpy.nan
                         for x in self.balance_range.balances.values()]
            width = 0.3
            axs.bar(ind - (width / 2.0), increases, width, label="total")
            normalised_increases = [x.total_increase_normalised if x.total_increase else numpy.nan
                                    for x in self.balance_range.balances.values()]
            axs.bar(ind + (width / 2.0), normalised_increases, width, label="normalised")
            fig.legend(loc="upper left")
        return self._setup_graph(_)
