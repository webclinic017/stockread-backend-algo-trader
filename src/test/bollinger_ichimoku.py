import backtrader as bt
from backtrader import Trade
from df_data_test import df as test_df
import pytz


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('printlog', False),  # Stop printing the log of the trading strategy

    )

    def __init__(self):

        self.dataclose= self.datas[0].close    # Keep a reference to the "close" line in the data[0] dataseries
        self.order = None # Property to keep track of pending orders.  There are no orders when the strategy is initialized.
        self.buyprice = None
        self.buycomm = None

        self.ichimoku = bt.indicators.Ichimoku(self.datas[0])

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint: # Add if statement to only log of printlog or doprint is True
            dt = dt or self.datas[0].datetime.datetime(0)
            print(f'{dt.isoformat()}, {txt}')



    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # not issue an order if there is an order is already in process
        if self.order:
            return

        # not issue an order if we're already in a position
        # if not in a position, then proceed with the buy
        if not self.position:

            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close

                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.log('BUY CREATED, %.2f' % self.dataclose[0])
                    # to store the sell order
                    self.order = self.buy()


        # else:
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('SELL CREATED {}'.format(self.dataclose[0]))
                # to store the buy order
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
