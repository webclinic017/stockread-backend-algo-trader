from src.autotrade.autotrader import AutoTrader
from src.autotrade.broker.wsimple_broker import WSimpleBroker
from src.autotrade.broker_conn.wsimple_conn import ConnectionWST
from src.autotrade.artifacts.quoter import QuestradeQuoter
from src.autotrade.artifacts.sizer import Sizer
from src.autotrade.strategy.strat_rsi import RSIStrategy
from src.autotrade.trade import Trade
from src.datafeed.yahoofinance.yf_single import PublicApiYF


def algo():
    auto_trader = AutoTrader()

    # set our desired cash start
    auto_trader.set_cash(10000.0)

    # create a trade bot
    trade_bot = Trade(codename='ac_tradebot', is_live_trade=True, trading_symbol='AC', ticker_alias='AC.TO',
                      currency='CAD')

    # add a quoter
    qt_quoter = QuestradeQuoter()
    trade_bot.set_quoter(quoter=qt_quoter)

    # add a sizer
    sizer = Sizer(is_by_size=True)
    sizer.add_size(value=1)
    trade_bot.set_sizer(sizer=sizer)

    # add a datafeed
    datafeed = PublicApiYF('AC.TO', interval='1m', period='1d')
    trade_bot.set_data(datafeed=datafeed)

    # add a broker
    conn_wst = ConnectionWST()
    conn_wst.connect()
    wst_auth = conn_wst.wst_auth

    brok_wst = WSimpleBroker()
    brok_wst.set_connection(wst_auth)
    brok_wst.set_trading_account("tfsa-hyrnpbqo")
    trade_bot.set_broker(broker=brok_wst)

    # add a strategy
    rsi_strategy = RSIStrategy()
    trade_bot.set_strategy(rsi_strategy)
    trade_bot.execute()

    # # Create a Data Feed
    # data = bt.feeds.PandasData(
    #     dataname=test_df,
    #     name='SHOP.TO', tz=pytz.timezone('America/Montreal'))
    #
    # # Add the Data Feed to Cerebro
    # cerebro.adddata(data)
    #
    # # Set our desired cash start
    # cerebro.broker.setcash(6000.0)
    #
    # # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.FixedSize, stake=4)
    #
    # # Set the commission - 0.1% ... divide by 100 to remove the %
    # cerebro.broker.setcommission(commission=0.000)
    #
    # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #
    # cerebro.run()
    #
    # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
    algo()
