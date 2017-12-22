'''
Backtrader analyzer for plotting using Bokeh interactive plotting library

Created: 2017-12-16
Updated: 2017-12-21

Created by ab-trader
'''

from __future__ import (absolute_import, division, print_function, unicode_literals)

from bokeh.models.widgets import Panel, Tabs
from bokeh.io import output_file, show
from bokeh.plotting import figure

__version__ = '0.4.105'

class btBokehPlot():

    def __init__(self, **kwargs):

        print('Bokeh plotter version %s' % __version__)


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

        output_file('strategy_%d.html' % figid)
        
        strategy_tabs = []
        strategy_tabs.append(self.broker_tab(name='BROKER'))

        for data in strategy.datas:
            strategy_tabs.append(self.data_tab(data=data))
        
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
        tab = Panel(child=self.quotes_plot(data), title=data._name)

        return tab


    def quotes_plot(self, data):
        '''
        Creates quotes figure based on backtrader's datafeed "data"
        '''
        quotes_fig = figure(plot_width=300, plot_height=300)
        quotes_fig.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)

        return quotes_fig


    def volume_plot(self, data, connected_data_figure):
        '''
        Creates volume figure connected to "data" figure based on backtrader's datafeed "data"
        '''
        volume_fig = figure(plot_width=300, plot_height=300)
        volume_fig.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)

        return volume_fig