import backtrader as bt
from df_data_test import df as test_df
import pytz


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('printlog', True),  # Stop printing the log of the trading strategy
        ('period', 14)

    )

    def __init__(self):

        self.dataclose= self.datas[0].close    # Keep a reference to the "close" line in the data[0] dataseries
        self.order = None # Property to keep track of pending orders.  There are no orders when the strategy is initialized.
        self.buyprice = None
        self.buycomm = None

        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.period)

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint: # Add if statement to only log of printlog or doprint is True
            dt = dt or self.datas[0].datetime.datetime(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order._status in [order.Submitted, order.Accepted]:
            return

        if order._status in [order.Completed]:
            if order._isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Size %d, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed._size,
                     order.executed.value,
                     order.executed.comm))
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Size %d, Revenue: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed._size,
                     order.executed.value,
                     order.executed.comm))

        elif order._status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f, RSI, %.2f' % (self.dataclose[0], self.rsi[0]))

        # not issue an order if there is an order is already in process
        if self.order:
            return

        # not issue an order if we're already in a position
        # if not in a position, then proceed with the buy
        if not self.position:

            if self.dataclose[0] < self.dataclose[-1]:
                if self.rsi[0] < 30:
                    self.log('BUY CREATED, %.2f' % self.dataclose[0])
                    self.order = self.buy()

        else:
            if self.rsi[0] > 70:
                self.log('SELL CREATED, %.2f' % self.dataclose[0])
                self.order = self.sell()


if __name__ == '__main__':
    test_df.drop('timestamp', axis=1, inplace=True)
    test_df.set_index('datetime', inplace=True)
    print(test_df)

    cerebro = bt.Cerebro()
    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Create a Data Feed
    data = bt.feeds.PandasData(
        dataname=test_df,
        name='SHOP.TO', tz=pytz.timezone('America/Montreal'))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(6000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=4)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # cerebro.plot()
