

from src.autotrade.artifacts.sizer import Sizer
from src.autotrade.broker.back_broker import BackBroker
from src.autotrade.strategy.rsi_strategy import RSICloudBollStrategy
from src.autotrade.trade import Trade

ac_tradingbot = Trade(codename='AC.TO_20210804', is_live_trade=False, trading_symbol='AC', ticker_alias='AC.TO',
                      currency='CAD', interval_option='5m', candle_count=500,
                      exchange='TSX', reps=2)

barfeed = ac_tradingbot.barfeed
# print(barfeed.latest_bar)
# print(barfeed.last_valid_bar)
# print(barfeed.bar_time_gap)
# print(ac_tradingbot.bar_time_gap)
# print(ac_tradingbot.interval)


ac_tradingbot.set_broker(BackBroker())
ac_tradingbot.set_sizer(Sizer(isbysize=True, size=100))
ac_tradingbot.set_strategy(RSICloudBollStrategy())
ac_tradingbot.set_stp_pricer()
ac_tradingbot.execute()




# sec = brok_wst.connection.find_securities_by_id('sec-s-5d572b2d37f64d09b26fbb20ea5c1e34')
# print(sec)
# cts = brok_wst.connection.find_securities('CTS', fuzzy=True)
# print(cts)

# id = 'order-33d352ad-0ab2-468f-931c-ebd9b6514826'

# new_order = Order(action=OrderAction.BUY, order_type=OrderType.MARKET, size=100,
#                   trading_symbol='AC', ticker_id='Unknown')
#
# new_order.ref_id = id
# new_order.ticker_id = 'sec-s-6e73535b8e474d8689064c4c9fee326a'
# print(new_order)
#
# tbot.set_broker(brok_wst)
# print(brok_wst.update_order_info(new_order))
# get_pending_orders = brok_wst.get_pending_orders()

# print(get_pending_orders)
# brok_wst.update_order_info(get_pending_orders)
# print(brok_wst.buying_power)
# print(brok_wst.get_position())
# order = brok_wst.market_buy(1)
# print(order)
#
# results = brok_wst.get_order_info(order)
# print(results)

# utcts = datetime.datetime.utcnow().timestamp()
# ts = datetime.datetime.now().timestamp()
# print(datetime.datetime.utcnow())
# print(datetime.datetime.now())
# print(utcts)
# print(ts)