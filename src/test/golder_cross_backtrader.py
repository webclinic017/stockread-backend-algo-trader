import math
import backtrader as bt
import pytz

from src.test import df as test_df


class Strat2_BGTMA_SLSMA(bt.Strategy):
    params = (
        ('maperiod', 15),  # Tuple of tuples containing any variable settings required by the strategy.
        ('printlog', False),  # Stop printing the log of the trading strategy

    )

    def __init__(self):
        self.dataclose = self.datas[0].close  # Keep a reference to the "close" line in the data[0] dataseries
        self.order = None  # Property to keep track of pending orders.  There are no orders when the strategy is initialized.
        self.buyprice = None
        self.buycomm = None

        # Add SimpleMovingAverage indicator for use in the trading strategy
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:  # Add if statement to only log of printlog or doprint is True
            dt = dt or self.datas[0].datetime.date(0)
            print('{0},{1}'.format(dt.isoformat(), txt))

    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing
        if order._status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order._status in [order.Completed]:
            if order._isbuy():
                self.log('BUY EXECUTED, Price: {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm: {3:8.2f}'.format(
                    order.executed.price,
                    order.executed._size,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, {0:8.2f}, Size: {1:8.2f} Cost: {2:8.2f}, Comm{3:8.2f}'.format(
                    order.executed.price,
                    order.executed._size,
                    order.executed.value,
                    order.executed.comm))

            self.bar_executed = len(self)  # when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order._status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(
            trade.pnl, trade.pnlcomm))

    def next(self):
        # Log the closing prices of the series from the reference
        self.log('Close, {0:8.2f}'.format(self.dataclose[0]))

        if self.order:  # check if order is pending, if so, then break out
            return

        # since there is no order pending, are we in the market?
        if not self.position:  # not in the market
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.buy()
        else:  # in the market
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, {0:8.2f}'.format(self.dataclose[0]))
                self.order = self.sell()

    def stop(self):
        self.log('MA Period: {0:8.2f} Ending Value: {1:8.2f}'.format(
            self.params.maperiod,
            self.broker.getvalue()),
            doprint=True)

class BuyHold(bt.Strategy):
    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        print("next start")
        # Buy all the available cash
        print(self.broker.get_cash())
        size = int(self.broker.get_cash() / self.data)
        self.buy(size=size)

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))


class GoldenCross(bt.Strategy):
    params = (('fast', 20),
              ('slow', 50),
              ('order_pct', 0.95),
              ('ticker', 'SPY'))

    def __init__(self):
        self.fastma = bt.indicators.SimpleMovingAverage(
            # self.datas[0],
            self.data.close,
            period=self.p.fast,
            plotname='50 day'
        )
        datas = self.datas[0]
        dataclose = self.data.close
        dataopen = self.data.open
        dataonly = self.data
        print(datas.high[0])
        print(datas.high[1])
        print(datas.array)
        print(dataclose.array)
        self.slowma = bt.indicators.SimpleMovingAverage(
            # self.datas[0],
            self.data.close,
            period=self.p.slow,
            plotname='200 day'
        )

        self.crossover = bt.indicators.CrossOver(
            self.fastma,
            self.slowma
        )


    def next(self):
        if self.position._size == 0:
            print("Cross-over value: {}".format(self.crossover))
            if self.crossover > 0:
                amount_to_invest = (self.p.order_pct * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares of {} at {}".format(self.size, self.p.ticker, self.data.close[0]))
                self.buy(size=self.size)

        if self.position._size > 0:
            if self.crossover < 0:
                print("Sell {} shares of {} at {}".format(self.size, self.p.ticker, self.data.close[0]))
                self.close()


if __name__ == '__main__':
    test_df.drop('timestamp', axis=1, inplace=True)
    test_df.set_index('datetime', inplace=True)

    cerebro = bt.Cerebro()
    # Add a strategy

    cerebro.addstrategy(GoldenCross)

    # Create a Data Feed
    data = bt.feeds.PandasData(
        dataname=test_df,
        name='SHOP.TO', tz=pytz.timezone('America/Montreal'))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(6000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # cerebro.plot()
