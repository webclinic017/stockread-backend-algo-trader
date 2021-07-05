import pytz

from df_data_test import df as test_df

# Import the backtrader platform
import backtrader as bt

bt.Sizer
bt.Order
bt.BrokerBase

# Create a Stratey
class TestStrategy(bt.Strategy):

    def __init__(self):
        print('init')

        self.bt_sma = bt.indicators.MovingAverageSimple(self.data, period=24)
        self.buy_sell_signal = bt.indicators.CrossOver(self.data.close, self.bt_sma)

    def start(self):
        print('The world call me!')

    def prenext(self):
        print('Not mature')

    def nextstart(self):
        print('Rites of passage')

    def next(self):
        # print('A new bar')
        # print(self.data.close[0])
        # ma_value = sum([self.data.close[-cnt] for cnt in range(24)])/24
        # ma_value = self.bt_sma[0]
        # pre_ma_value = self.bt_sma[-1]
        #
        # if self.data.close[0] > ma_value and self.data.close[-1] <= pre_ma_value:
        #     print('long', self.data.datetime.datetime())
        #     self.order = self.buy()
        #
        # if self.data.close[0] < ma_value and self.data.close[-1] >= pre_ma_value:
        #     print('short', self.data.datetime.datetime())
        #     self.order = self.sell()

        if not self.position and self.buy_sell_signal[0] == 1:
            self.order = self.buy()

        if not self.position and self.buy_sell_signal[0] == -1:
            self.order = self.sell()

        if self.position and self.buy_sell_signal[0] == 1:
            self.order = self.close()
            self.order = self.buy()

        if self.position and self.buy_sell_signal[0] == -1:
            self.order = self.close()
            self.order = self.sell()

    def stop(self):
        print('I should leave the world')


if __name__ == '__main__':
    test_df.drop('timestamp', axis=1, inplace=True)
    test_df.set_index('datetime', inplace=True)

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
    cerebro.addsizer(bt.sizers.FixedSize, stake=3)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.000)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
