from src.autotrade.artifacts.sizer import Sizer
from src.autotrade.broker.wsimple_broker import WSimpleBroker
from src.autotrade.broker_conn.wsimple_conn import ConnectionWST
from src.autotrade.strategy.strat_base import BaseStrategy
from src.autotrade.trade import Trade, IntervalOption

ac_tradingbot = Trade(codename='AC.TO_20210804', is_live_trade=True, trading_symbol='AC', ticker_alias='AC.TO',
                      currency='CAD', data_interval=IntervalOption.I_5MINS, interval_number=300,
                      exchange='TSX', reps=1)

barfeed = ac_tradingbot.barfeed
# print(barfeed.latest_bar)
# print(barfeed.last_valid_bar)
# print(barfeed.bar_time_gap)
# print(ac_tradingbot.bar_time_gap)
# print(ac_tradingbot.interval)


strategy = BaseStrategy()

conn_wst = ConnectionWST()
conn_wst.connect()
wst_auth = conn_wst.wst_auth
brok_wst = WSimpleBroker()
brok_wst.set_connection(wst_auth)
brok_wst.set_trading_account("tfsa-hyrnpbqo")
ac_tradingbot.set_broker(brok_wst)
# ac_tradingbot.set_broker(BackBroker())
ac_tradingbot.set_sizer(Sizer(is_by_size=True))
ac_tradingbot.set_strategy(strategy)
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