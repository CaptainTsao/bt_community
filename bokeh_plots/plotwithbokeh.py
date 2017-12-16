'''
Backtrader analyzer for plotting using Bokeh interactive plotting library

Created: 2017-12-16
Updated: 2017-12-16

Created by ab-trader
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)

__version__ = '0.1.53'

import backtrader as bt
import bokeh.plotting as bp

class BokehPlot(bt.Analyzer):

    params = (('html_name', 'default_plot.html'),
              ('html_title', 'default plot'),)

    def __init__(self):

        self.equity = []
        self.cash = []
        self.datetime = []

    def track_data(self):

        self.equity.append(self.strategy.broker.get_value())
        self.cash.append(self.strategy.broker.get_cash())
        self.datetime.append(bt.num2date(self.strategy.datetime[0]))

    def prenext(self):

        self.track_data()

    def next(self):

        self.track_data()

    def stop(self):

        equity_figure = bp.figure(x_axis_type="datetime",
                                  x_range=[self.datetime[0], self.datetime[-1]],
                                  plot_width=1000, plot_height=400,
                                  title = 'Equity Curve, $')
        equity_figure.multi_line(xs=[self.datetime, self.datetime],
                                 ys=[self.equity, self.cash],
                                 color=['darkgreen','blue'])

        bp.output_file(self.p.html_name, title=self.p.html_title)
        bp.show(equity_figure)