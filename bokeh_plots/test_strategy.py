from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime as dt
import pandas as pd

import time
import os.path
import argparse
import logging

import backtrader as bt
import plotwithbokeh as pwb

# set initial parameters
INITIAL_CASH = 50000.0          # inital capital
DB_PATH = 'C:\Futures_quotes'   # path to local quotes database

# read specifications for futures
FUT_SPECS = pd.read_csv('fut_specs.txt')

# read all trades made during tests
columns_to_read = ['Trade #', 'Futures', 'Mult', 'Date in', 'Date out', 'Dir', 'Price in',
                    'Price out']
FUT_TRADES = pd.read_csv('trades.csv', usecols=columns_to_read, na_filter=False)
Orders = []
for i, row in FUT_TRADES.iterrows():
    if row['Date in'] != '':
        Orders.append((dt.datetime.strptime(row['Date in'], '%m-%d-%Y'),
                      int(row['Dir']), float(row['Price in']), row['Futures']))
    if row['Date out'] != '':
        Orders.append((dt.datetime.strptime(row['Date out'], '%m-%d-%Y'),
                      -int(row['Dir']), float(row['Price out']), row['Futures']))

def byDate(rec): return rec[0]

Orders = sorted(Orders, key=byDate)
OrdersTuple = tuple(Orders)

# script arguments parser, returns arguments as namespace
def parse_args(pargs=None):

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=('Strategy auto-generation framework'))

    parser.add_argument('--log', required=False,
                        default="level='all', filename='',  filemode=''",
                        help='specify logging level (RESULTS, TRADES, ORDERS, ORDERS_FULL, ' + \
                             'SIGNALS, ALL), log file name and log mode (overwrite ''w'' or ' + \
                             'append ''a'')')

    return parser.parse_args(pargs)

# logging facility setup; returns logger
def logger_setup(**kwargs):

    logging.basicConfig(format='%(message)s (%(funcName)s)',
                        filename=kwargs['filename'], filemode=kwargs['filemode'])

    levels = {}
    levels['RESULTS'] = logging.RESULTS = 100
    levels['TRADES'] = logging.TRADES = 80
    levels['ORDERS'] = logging.ORDERS = 60
    levels['ORDERS_FULL'] = logging.ORDERS_FULL = 40
    levels['SIGNALS'] = logging.SIGNALS = 20
    levels['ALL'] = logging.ALL = 10

    logger = logging.getLogger(__name__)
    logger.setLevel(level=getattr(logging, kwargs['level'].upper()))
    logger.log(logging.ALL, 'Effective logger level =  %d' % logger.getEffectiveLevel())

    return logger, levels

# parse script arguments & setup logger
args = parse_args(None)
logger, lvl = logger_setup(**(eval('dict(' + args.log + ')')))

# master strategy
class MasterStrategy(bt.Strategy):
   
    def __init__(self):

        self.order, self.trade_size, self.pos_length, self.bar_executed = {}, {}, {}, {}

        for i, d in enumerate(self.datas):

            dn = d._name
            self.order[dn] = None

        
    def notify_trade(self, trade):

        dt, dn = trade.data.datetime.date(0).isoformat(), trade.data._name

        if trade.justopened:

            self.trade_size[dn] = trade.size

        if trade.isclosed:

            logger.log(lvl['TRADES'],
                       '%s %s: Trade, Gross P/L, %.2f, Net P/L, %.2f, Size, %d, Length, %d' %
                       (dt, dn, trade.pnl, trade.pnlcomm, self.trade_size[dn], trade.barlen))


    def notify_order(self, order):

        dt, dn = order.data.datetime.date(0).isoformat(), order.data._name

        logger.log(lvl['ORDERS_FULL'], '%s %s: Order %s, Price %.4f, Size %d, Ref %s' %
                    (dt, dn, order.getstatusname().lower(), order.created.price,
                     order.created.size, order.ref))


    def next(self):

        logger.log(lvl['ALL'], 'cash, %0.2f, value, %0.2f' % (self.broker.getcash(),
                                                              self.broker.getvalue()))

        for i, d in enumerate(self.datas):

            dn, pos = d._name, self.getposition(d)

            logger.log(lvl['ALL'], '%s %s: size, %d, '
                       % (d.datetime.date(0).isoformat(), dn, pos.size) +
                       ' O, %0.4f, H, %0.4f, L, %0.4f, C, %0.4f, V, %d' %
                       (d.open[0], d.high[0], d.low[0], d.close[0], d.volume[0]))


if __name__ == '__main__':

    print('backtrader, version %s' % bt.__version__)
    print('plotwithbokeh, version %s' % pwb.__version__)

    startTime = time.time()

    # initialize and run backtest engine
    cerebro = bt.Cerebro()

    # add analyzers
#    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
#    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(pwb.BokehPlot, _name='bp')

    # add data feeds and set comissions
    for index, contract in FUT_SPECS.iterrows():

        show_data = bool(int(contract['show or not']))
        datapath = os.path.join(DB_PATH,
                                contract['exchange'] + '-' + contract['quandl_name'] + 'r.csv')

        data = bt.feeds.GenericCSVData(dataname=datapath, 

            fromdate=dt.datetime(2017, 9, 1),
            todate=dt.datetime(2017, 12, 31),

            nullvalue=0.0,

            dtformat=('%Y-%m-%d'),

            datetime=0, open=1, high=2, low=3, close=4, change=5, settle=6, volume=7,
            openinterest=8,

            plot=show_data, name=contract['name'])

        cerebro.adddata(data)

        cerebro.broker.setcommission(commission=float(contract['comm']),
                                     margin=float(contract['margin']),
                                     mult=float(contract['mult']),
                                     name=contract['name'])

    # add strategy
    cerebro.addstrategy(MasterStrategy)

    # add order history
    cerebro.add_order_history(OrdersTuple, notify=True)

    cerebro.broker.set_cash(INITIAL_CASH)
    strats = cerebro.run()

    ## gather trading system statistics
    #cum_pnl = cerebro.broker.getvalue() - INITIAL_CASH
    #stats = {}

    ## drawdown statistics
    #dds = strats[0].analyzers.dd.get_analysis()
    #stats['maxdd'] = dds['max']['moneydown']
    #stats['maxdd%'] = dds['max']['drawdown']
    #stats['maxdd_len'] = dds['max']['len']

    ## trades statistics
    #trades = strats[0].analyzers.trades.get_analysis()
    #stats['win_rate'] = stats['avg_trade'] = 0.0
    #stats['avg_win'] = stats['avg_loss'] = stats['avg_wl_rate'] = 0.0
    #stats['trades'] = stats['max_loss_streak'] = 0
    #if trades['total']['total'] != 0 and trades['total']['total'] != trades['total']['open']:
    #    stats['trades'] = trades['total']['total']
    #    stats['win_rate'] = trades['won']['total'] / trades['total']['total'] * 100
    #    stats['avg_trade'] = trades['pnl']['net']['average']
    #    stats['avg_win'] = trades['won']['pnl']['average']
    #    stats['avg_loss'] = trades['lost']['pnl']['average']
    #    stats['avg_wl_rate'] = 1000.0
    #    if stats['avg_loss'] != 0.0:
    #        stats['avg_wl_rate'] = abs(stats['avg_win'] / stats['avg_loss'])
    #    stats['max_loss_streak'] = trades['streak']['lost']['longest']

    #stats['calmar'] = cum_pnl / stats['maxdd'] if stats['maxdd'] != 0.0 else 10000.0

    #sec1 = 'return, %0.2f, max DD, %0.2f, calmar, %0.2f, dd max len, %d,' % (
    #        cum_pnl, stats['maxdd'], stats['calmar'], stats['maxdd_len'])

    #sec2 = ' trades, %d, win%%, %0.1f, avg, %d, win, %d, loss, %d,' % (
    #        stats['trades'], stats['win_rate'], stats['avg_trade'], stats['avg_win'],
    #        stats['avg_loss'])

    #sec3 = ' win/loss, %0.2f, max loss streak, %d,' % (
    #        stats['max_loss_streak'], stats['avg_wl_rate'])

    #logger.log(lvl['RESULTS'], sec1 + sec2 + sec3)

    #logger.log(lvl['RESULTS'], 'it took {0} second !'.format(time.time() - startTime))

    #cerebro.plot(style='candle', numfigs=1,
    #             barup = 'black', bardown = 'black',
    #             barupfill = False, bardownfill = True,
    #             volup = 'green', voldown = 'red', voltrans = 50.0, voloverlay = False)