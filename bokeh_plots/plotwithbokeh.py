'''
Backtrader plotter using Bokeh interactive plotting library

Created: 2017-12-16
Updated: 2017-12-22

Created by ab-trader
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bokeh.models.widgets import Panel, Tabs
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.layouts import gridplot

from math import pi

import backtrader as bt
import pandas as pd
import pdb

__version__ = '0.5.156'

class btBokehPlot():

    def __init__(self, **kwargs):

        self.width = 800
        self.q_height = 300
        self.v_height = 150


    def plot(self, strategy, figid=0, numfigs=1, iplot=True, start=None, end=None, use=None):
        '''
        Creates html file with bokeh plot for single "strategy"
        "figid": strategy id
        "numfigs": irrelevant for bokeh, left for compatibility with cerebro.plot()
        "iplot": irrelevant, doesn't support jupyter notebook yet
        "start": an index to the datetime line array of the strategy or a datetime.date,
        datetime.datetime instance indicating the start of the plot
        "end": an index to the datetime line array of the strategy or a datetime.date,
        datetime.datetime instance indicating the end of the plot
        "use": irrelevant for bokeh, left for compatibility with cerebro.plot()
        '''
        if not strategy.datas:
            return

        if not len(strategy):
            return

        self.dt_axis = [bt.num2date(x) for x in strategy.datetime.array.tolist()]

        output_file('strategy_%d.html' % figid, title='strategy #%d' % figid)
        
        strategy_tabs = []
        strategy_tabs.append(self.broker_tab(name='BROKER'))

        for data in strategy.datas:
            if data.plotinfo.plot:
                strategy_tabs.append(self.data_tab(data=data))
        
        if not len(strategy_tabs):
            return

        tabs = Tabs(tabs=strategy_tabs)
        
        show(tabs)

        return tabs


    def show(self):
        '''
        Irrelevant, left for compatibilty with cerebro.plot()
        '''
        return

    
    def broker_tab(self, name):
        '''
        Creates tab with broker related diagrams such as equity, return, cash, drawdowns and
        benchmark.
        "name" is the name of the tab
        '''
        p = figure(plot_width=300, plot_height=300)
        p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
        tab = Panel(child=p, title=name)

        return tab


    def data_tab(self, data):
        '''
        Creates tab with data feed (prices) diagram shown in candle format.
        "name" is the name of the tab
        '''
        # prepare data
        df = pd.DataFrame(index=xrange(len(data)))
        df['open'] = data.open.array.tolist()
        df['high'] = data.high.array.tolist()
        df['low'] = data.low.array.tolist()
        df['close'] = data.close.array.tolist()
        df['volume'] = data.volume.array.tolist()
        dt_list = [bt.num2date(x) for x in data.datetime.array.tolist()]
        df['dt'] = dt_list

        quotes = self.candles_plot(df)
        volume = self.volume_plot(df, quotes)

        grid = gridplot([quotes, volume], ncols=1)
        tab = Panel(child=grid, title=data._name)

        return tab


    def candles_plot(self, df):
        '''
        Creates candlestick figure for backtrader's datafeed "data"
        '''
        inc = df.close > df.open
        dec = df.open > df.close
        w = 12*60*60*1000 # half day in ms

        fig = figure(x_axis_type="datetime", plot_width=self.width, plot_height=self.q_height,
                     x_range=[self.dt_axis[0], self.dt_axis[-1]])
        fig.xaxis.major_label_orientation = pi/4
        fig.grid.grid_line_alpha=1.0

        fig.segment(df.dt, df.high, df.dt, df.low, color="black")
        fig.vbar(df.dt[inc], w, df.open[inc], df.close[inc],
                 fill_color="white", line_color="black")
        fig.vbar(df.dt[dec], w, df.open[dec], df.close[dec],
                 fill_color="#2d2d2d", line_color="black")

        return fig


    def volume_plot(self, df, connected_data_figure):
        '''
        Creates volume figure connected to "data" figure for backtrader's datafeed "data"
        '''
        inc = df.close > df.open
        dec = df.open > df.close
        w = 18*60*60*1000 # half day in ms

        fig = figure(x_axis_type="datetime", plot_width=self.width, plot_height=self.v_height,
                     x_range=connected_data_figure.x_range)
        fig.xaxis.major_label_orientation = pi/4
        fig.grid.grid_line_alpha=1.0
        fig.vbar(df.dt[inc], w, 0, df.volume[inc], fill_color="white", line_color="black",
                 line_width=0.5)
        fig.vbar(df.dt[dec], w, 0, df.volume[dec], fill_color="#2d2d2d", line_color="black",
                 line_width=0.5)

        return fig