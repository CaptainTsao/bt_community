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

# Last close indicator
class LastClose(bt.Indicator):

    lines = ('close',)
    params = (('period', 0),)

    def __init__(self):

        self.lines.close = self.data.close(-self.p.period)


# master strategy
class MasterStrategy(bt.Strategy):
   
    def __init__(self):

        self.lclose = lclose = LastClose(self.datas[1])
        lclose.plotinfo.subplot = False
        lclose1 = lclose()
        lclose1.plotinfo.subplot = False


if __name__ == '__main__':

    print('backtrader, version %s' % bt.__version__)

    # initialize and run backtest engine
    cerebro = bt.Cerebro()

    tickers = ['ESZ2017']

    # add data feeds and set comissions
    for ticker in tickers:

        datapath = os.path.join(DB_PATH,QUANDL_DB + '-' + ticker + 'r.csv')

        data = bt.feeds.GenericCSVData(dataname=datapath, 

            fromdate=dt.datetime(2017, 10, 1),
            todate=dt.datetime(2017, 12, 31),

            nullvalue=0.0,

            dtformat=('%Y-%m-%d'),

            datetime=0, open=1, high=2, low=3, close=4, change=5, settle=6, volume=7,
            openinterest=8,

            plot=True, name=ticker)

        cerebro.adddata(data)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)

    # add strategy
    cerebro.addstrategy(MasterStrategy)

    strats = cerebro.run()

    cerebro.plot(style='candle', numfigs=1,
                 barup = 'black', bardown = 'black',
                 barupfill = False, bardownfill = True,
                 volup = 'green', voldown = 'red', voltrans = 50.0, voloverlay = False)