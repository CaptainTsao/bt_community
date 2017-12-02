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


class PivotPointIndicator(bt.Indicator):

    lines =('r3', 'r2', 'r1', 'pp', 's1', 's2', 's3',)
    params = dict(withopen=True)
    plotinfo = dict(subplot=False)

    def __init__(self):
        h = self.data.high
        l = self.data.low
        c = self.data.close

        if not self.p.withopen:
            self.lines.pp = pp = (h + l + c) / 3.0
        else:
            o = self.data.open
            self.lines.pp = pp = (o + h + l + c) / 4.0

        p2 = pp * 2.0
        self.lines.s1 = p2 - h  # (p x 2) - high
        self.lines.r1 = p2 - l  # (p x 2) - low

        hilo = h - l
        self.lines.s2 = pp - hilo  # p - (high - low)
        self.lines.r2 = pp + hilo  # p + (high - low)

        self.lines.r3 = h + 2 * (pp - l)
        self.lines.s3 = l - 2 * (h - pp)


# master strategy
class MasterStrategy(bt.Strategy):

    def __init__(self):

        self.pivots_weekly = PivotPointIndicator(self.datas[0])
        self.pivots_monthly = PivotPointIndicator(self.datas[1])

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):

        self.log('L1: {}, L2: {}, PP Reversals: weekly: {}, monthly: {}'.format(len(self.datas[0]), len(self.datas[1]),
                                                                        self.pivots_weekly.l.pp[0], self.pivots_monthly.l.pp[0]))
        #self.log('close: daily: {}, weekly: {}, monthly: {}'.format(self.datas[0].close[0], self.datas[1].close[0],
        #                                                            self.datas[2].close[0]))


if __name__ == '__main__':

    print('backtrader, version %s' % bt.__version__)

    # initialize and run backtest engine
    cerebro = bt.Cerebro()

    tickers = ['ESZ2017']

    # add data feeds and set comissions
    for ticker in tickers:

        datapath = os.path.join(DB_PATH,QUANDL_DB + '-' + ticker + 'r.csv')

        data = bt.feeds.GenericCSVData(dataname=datapath, 

            fromdate=dt.datetime(2017, 5, 28),
            todate=dt.datetime(2017, 11, 3),

            nullvalue=0.0,

            dtformat=('%Y-%m-%d'),

            datetime=0, open=1, high=2, low=3, close=4, change=5, settle=6, volume=7,
            openinterest=8,

            plot=True, name=ticker)

#        cerebro.adddata(data)
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks, compression=1)
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Months, compression=1)

    # add strategy
    cerebro.addstrategy(MasterStrategy)

    strats = cerebro.run(stdstats=False)

    cerebro.plot(style='candle', numfigs=1,
                 barup = 'black', bardown = 'black',
                 barupfill = False, bardownfill = True,
                 volup = 'green', voldown = 'red', voltrans = 50.0, voloverlay = False)
