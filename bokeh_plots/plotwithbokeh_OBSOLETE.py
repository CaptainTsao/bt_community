'''
Backtrader analyzer for plotting using Bokeh interactive plotting library

Created: 2017-12-16
Updated: 2017-12-16

Created by ab-trader
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)

__version__ = '0.2.102'

import backtrader as bt
import bokeh.plotting as bp

import pdb

class BokehPlot(bt.Analyzer):

    params = (('html_name', 'default_plot.html'),
              ('html_title', 'default plot'),
              ('plot_w', 1000),
              ('plot_h', 400),)

    def __init__(self):

        # init variables
        self.equity, self.cash, self.datetime = [], [], []
        self.ddd, self.maxddd, self.ddp, self.maxddp = [], [], [], []

        # add drawdown analyzer
        self._dd = self.strategy._addanalyzer_slave(bt.analyzers.DrawDown)

    def track_data(self):

        self.equity.append(self.strategy.broker.get_value())
        self.cash.append(self.strategy.broker.get_cash())
        self.datetime.append(bt.num2date(self.strategy.datetime[0]))
        self.ddd.append(-self._dd.rets.moneydown)
        self.maxddd.append(-self._dd.rets.max.moneydown)
        self.ddp.append(-self._dd.rets.drawdown)
        self.maxddp.append(-self._dd.rets.max.drawdown)

    def prenext(self):

        self.track_data()

    def next(self):

        self.track_data()

    def stop(self):

        pdb.set_trace()

        x_range = [self.datetime[0], self.datetime[-1]]

        # equity/cash diagram
        y_range1 = [0.95 * min(min(self.equity), min(self.cash)),
                    1.05 * max(max(self.equity), max(self.cash))]

        equity_figure = bp.figure(x_range=x_range, y_range=y_range1, x_axis_type="datetime",
                                  plot_width=self.p.plot_w, plot_height=self.p.plot_h,
                                  title = 'Equity Curve, $')
        # equity filled area
        equity_figure.patch(self.datetime+[self.datetime[-1], self.datetime[0]],
                            self.equity+[0.0, 0.0], alpha=0.75, line_width=1.0, color='green')
        # margin/position size
        equity_figure.patch(self.datetime+self.datetime[::-1], self.equity+self.cash[::-1],
                            alpha=0.75, line_width=1.0, color='lightblue')
        # equity curve
        equity_figure.line(self.datetime, self.equity, color='darkgreen', line_width=2.0)

        # money drawdown diagram
        y_range2 = [1.05 * self.maxddd[-1], 0]

        ddd_figure = bp.figure(x_range=equity_figure.x_range, y_range=y_range2,
                              plot_width=self.p.plot_w, plot_height=int(self.p.plot_h/2.5),
                              x_axis_type="datetime", title = 'Drawdown, $')
        # money drawdown filled area
        ddd_figure.patch(self.datetime+[self.datetime[-1], self.datetime[0]],
                         self.ddd+[0.0, 0.0], alpha=0.25, line_width=1.0, color='red')
        # money drawdown curve
        ddd_figure.line(self.datetime, self.ddd, color='red', line_width=2.0)
        # max money drawdown curve
        ddd_figure.line(self.datetime, self.maxddd,
                        color='black', line_width=1.0, line_dash='dashed')

        # percent drawdown diagram
        y_range3 = [1.05 * self.maxddp[-1], 0]

        ddp_figure = bp.figure(x_range=equity_figure.x_range, y_range=y_range3,
                              plot_width=self.p.plot_w, plot_height=int(self.p.plot_h/2.5),
                              x_axis_type="datetime", title = 'Drawdown, %')
        # percent drawdown filled area
        ddp_figure.patch(self.datetime+[self.datetime[-1], self.datetime[0]],
                         self.ddp+[0.0, 0.0], alpha=0.25, line_width=1.0, color='red')
        # percent drawdown curve
        ddp_figure.line(self.datetime, self.ddp, color='red', line_width=2.0)
        # max percent drawdown curve
        ddp_figure.line(self.datetime, self.maxddp,
                        color='black', line_width=1.0, line_dash='dashed')

        bp.output_file(self.p.html_name, title=self.p.html_title)
        bp.show(bp.gridplot([equity_figure, ddd_figure, ddp_figure], ncols=1))