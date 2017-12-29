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


# master strategy
class MasterStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        self.log('Daily OHLC: %0.2f, %0.2f, %0.2f, %0.2f; Weekly OHLC: %.2f, %0.2f, %0.2f, %0.2f'
                 % (self.datas[0].open[0], self.datas[0].high[0], self.datas[0].low[0],
                    self.datas[0].close[0], self.datas[1].open[0], self.datas[1].high[0],
                    self.datas[1].low[0], self.datas[1].close[0]))


if __name__ == '__main__':

    print('backtrader, version %s' % bt.__version__)

    # initialize and run backtest engine
    cerebro = bt.Cerebro()

    tickers = ['ESZ2017']

    # add data feeds and set comissions
    for ticker in tickers:

        datapath = os.path.join(DB_PATH,QUANDL_DB + '-' + ticker + 'r.csv')

        data = bt.feeds.GenericCSVData(dataname=datapath, 

            fromdate=dt.datetime(2017, 11, 25),
            todate=dt.datetime(2017, 12, 31),

            nullvalue=0.0,

            dtformat=('%Y-%m-%d'),

            datetime=0, open=1, high=2, low=3, close=4, change=5, settle=6, volume=7,
            openinterest=8,

            plot=True, name=ticker,
            
            timeframe=bt.TimeFrame.Days, compression=1)

        cerebro.adddata(data)

        cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks, boundoff=1)


    # add strategy
    cerebro.addstrategy(MasterStrategy)

    strats = cerebro.run()

    cerebro.plot(style='candle', numfigs=1,
                 barup = 'black', bardown = 'black',
                 barupfill = False, bardownfill = True,
                 volup = 'green', voldown = 'red', voltrans = 50.0, voloverlay = False)