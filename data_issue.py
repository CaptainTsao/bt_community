import backtrader as bt

class firstStrategy(bt.Strategy):

    def __init__(self):

        pass

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    startcash = 10000

    # Add a strategy
    cerebro.addstrategy(firstStrategy)

    # Create a Data Feed

    data = bt.feeds.GenericCSVData(
        dataname='prices_daily.csv',

        nullvalue=0.0,

#        dtformat=('%Y%m%d %H:%M:%S'),
        dtformat=('%Y%m%d'),

        datetime=0,
        time=-1,
        open=1,
        high=2,
        low=3,
        close=5,
        volume=-1,
        openinterest=-1,
#        timeframe=bt.TimeFrame.Minutes,
#        compression=60
        )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(startcash)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0005)

    # Add a sizer
    cerebro.addsizer(bt.sizers.PercentSizer, percents=50)

    cerebro.run()
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % startcash)

    # Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    # Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))

    # Finally plot the end results
    cerebro.plot()