import numpy
from matplotlib import pyplot
from matplotlib.ticker import FormatStrFormatter

from finance.finance_manager import BalanceRange, FinanceManager


class FinanceGraphManager:

    def __init__(self, balance_range: BalanceRange):
        self.balance_range = balance_range

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
            axs.axhline(y=0, color='black', linestyle='-')
            increases = [x.total_increase if x.total_increase else numpy.nan
                         for x in self.balance_range.balances.values()]
            width = 0.3
            axs.bar(ind - (width / 2.0), increases, width, label="total")
            normalised_increases = [FinanceManager.get_increase_after_normalisation(x)
                                    if x.total_increase else numpy.nan for x in self.balance_range.balances.values()]
            axs.bar(ind + (width / 2.0), normalised_increases, width, label="normalised")
            fig.legend(loc="upper left")
        return self._setup_graph(_)
