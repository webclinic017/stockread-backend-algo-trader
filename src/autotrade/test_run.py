from src.autotrade.broker.brok_wst import BrokerWST
from src.autotrade.broker.order import Order, OrderAction, OrderType
from src.autotrade.broker.wst_conn import ConnectionWST
from src.autotrade.tradebot import TradeBot, TradingMode

conn_wst = ConnectionWST()
conn_wst.connect()
wst_auth = conn_wst.wst_auth

brok_wst = BrokerWST()
brok_wst.set_connection(wst_auth)
brok_wst.set_trading_account("tfsa-hyrnpbqo")
# sec = brok_wst.connection.find_securities_by_id('sec-s-5d572b2d37f64d09b26fbb20ea5c1e34')
# print(sec)
# cts = brok_wst.connection.find_securities('CTS', fuzzy=True)
# print(cts)
tbot = TradeBot('TestRun', TradingMode.LIVE, 'AC', 'AC.TO', 'CAD')
id = 'order-33d352ad-0ab2-468f-931c-ebd9b6514826'

new_order = Order(action=OrderAction.BUY, order_type=OrderType.MARKET, size=100,
                          trading_symbol='AC', ticker_id='Unknown')

new_order.ref_id = id
new_order.ticker_id = 'sec-s-6e73535b8e474d8689064c4c9fee326a'
print(new_order)

tbot.set_broker(brok_wst)
print(brok_wst.update_order_info(new_order))
get_pending_orders = brok_wst.get_pending_orders()

# print(get_pending_orders)
# brok_wst.update_order_info(get_pending_orders)
# print(brok_wst.buying_power)
# print(brok_wst.get_position())
# order = brok_wst.market_buy(1)
# print(order)
#
# results = brok_wst.get_order_info(order)
# print(results)

