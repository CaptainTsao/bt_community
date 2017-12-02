from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime as dt
import pandas as pd

import time
import os.path

import backtrader as bt

# set initial parameters
INITIAL_CASH = 50000.0          # inital capital
QUANDL_DB = 'CME'               # quandl database for futures quotes
DB_PATH = 'C:\Futures_quotes'   # path to local quotes database

# ADX indicator which returns 3 lines for each output
class ADXDIPlus3(bt.Indicator):

    lines = ('high', 'low', 'close')

    params = (('period', 20),)

    def __init__(self):

        self.ADX = bt.indicators.DirectionalMovementIndex(period=self.p.period)

        self.lines.high = self.ADX.DIplus
        self.lines.low = self.ADX.DIplus
        self.lines.close = self.ADX.DIplus


# master strategy
class MasterStrategy(bt.Strategy):
   
    def __init__(self):

        self.CCI = bt.indicators.CommodityChannelIndex(period=20)
        self.ADX = bt.indicators.DirectionalMovementIndex(period=12)
        self.ADXPlus3 = ADXDIPlus3(period=12)
        self.CCI_ADXPlus = bt.indicators.CommodityChannelIndex(self.ADXPlus3, period=20)


if __name__ == '__main__':

    print('backtrader, version %s' % bt.__version__)

    # initialize and run backtest engine
    cerebro = bt.Cerebro()

    tickers = ['ESZ2017']

    # add data feeds and set comissions
    for ticker in tickers:

        datapath = os.path.join(DB_PATH,QUANDL_DB + '-' + ticker + 'r.csv')

        data = bt.feeds.GenericCSVData(dataname=datapath, 

            fromdate=dt.datetime(2017, 3, 1),
            todate=dt.datetime(2017, 12, 31),

            nullvalue=0.0,

            dtformat=('%Y-%m-%d'),

            datetime=0, open=1, high=2, low=3, close=4, change=5, settle=6, volume=7,
            openinterest=8,

            plot=True, name=ticker)

        cerebro.adddata(data)

    # add strategy
    cerebro.addstrategy(MasterStrategy)

    strats = cerebro.run()

    cerebro.plot(style='candle', numfigs=1,
                 barup = 'black', bardown = 'black',
                 barupfill = False, bardownfill = True,
                 volup = 'green', voldown = 'red', voltrans = 50.0, voloverlay = False)