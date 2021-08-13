import datetime
import time
import math
from abc import abstractmethod, ABC

from src.autotrade.bars.barfeed import BarFeed
from typing import TYPE_CHECKING, Optional, Union

from src.autotrade.broker.base_broker import IBroker, ILiveBroker
from src.autotrade.artifacts.order import OrderType, Order, OrderAction

if TYPE_CHECKING:
    from src.autotrade.trade import Trade
    from src.autotrade.artifacts.sizer import Sizer


class BaseStrategy(ABC):

    def __init__(self):
        # set from Trade class
        self._is_live = None
        self._trade_bot: Optional['Trade'] = None
        self._broker: Union[IBroker, ILiveBroker, None] = None
        self._sizer: Optional['Sizer'] = None
        self._trading_symbol = None
        self._position = None

        # BARS & BARS CONTROL
        self._barfeed: Optional[BarFeed] = None
        self._bars = None
        self._last_bar_timestamp = None
        self._next_bar_timestamp = None
        self._bar_time_gap = None

        # TODO: (1): add TrailingController instance (if required else)
        # TODO: (2): add logging and notify (notification)
        # TODO: (3): method prepare (setup) pretrade ... to setup trailing and indicator and signal
        # TODO: (4): next to run and update bars for live trading, test again real data
        # TODO: (5): implement notify signal method

    def bind_to_trade(self, trade_bot: 'Trade'):
        self._trade_bot = trade_bot
        self._broker = self._trade_bot.broker
        self._sizer = self._trade_bot.sizer
        self._barfeed = self._trade_bot.barfeed
        self._trading_symbol = self._trade_bot.trading_symbol
        self._is_live = self._trade_bot.is_live_trade
        self._position = self._trade_bot._position
        self.update_position()
        self._bar_time_gap = self._trade_bot.bar_time_gap

    @property
    def barfeed(self):
        if self._last_bar_timestamp != self._trade_bot.barfeed.last_bar.timestamp:
            self._barfeed = self._trade_bot.barfeed
            self._last_bar_timestamp = self._trade_bot.barfeed.latest_bar.timestamp
        return self._barfeed

    def __iter__(self):
        return self

    def __next__(self):
        self._bars = next(self.barfeed)
        self.pre_next()
        self.next()
        self.post_next()

    def getsizing(self, ref_price, isbuy=True):
        # TODO: (1): Implement isbuy check for False
        # TODO: (2): Implement isbuy check for BY.AMOUNT and BY.SIZE (if broker buy_power sufficient)
        # TODO: (3): Implement isbuy check for ref_price (if broker buy_power sufficient)

        if isbuy:
            if ref_price:
                return self._sizer.size
            else:
                return self._sizer.size
        else:
            return 0

    # if self._is_prep_done:
    #
    # else:
    #     raise Exception('It is required to run setup() first before running next()')

    @property
    def bars(self):
        return self._bars

    # @abstractmethod
    # def prepare(self):
    #     raise NotImplementedError()
    #
    # def setup(self):
    #     self.prepare()
    #     self._is_prep_done = True

    def pre_next(self):
        if self._is_live and self._trade_bot.active_order:
            if self._trade_bot.is_order_updatable():
                self.update_active_order(is_instant_update=True)
                if not self._trade_bot.active_order.is_settled():
                    self.cancel_active_order()
                    time.sleep(3)  # wait 3 seconds (or some time) for cancelling request to be processed by the broker
                    self.update_active_order(is_instant_update=True)

            if self._trade_bot.is_order_removable():
                self._trade_bot.remove_order()
            else:
                # TODO: implement unfilled pending order notification
                raise Exception('There is an unsettled order in the trade has not been remove.\n'
                                'It is required to remove the settled order before the next data refresh.\n'
                                'Please check the order removal logic & procedure.')

    # @abstractmethod
    def next(self):
        print(f'last bar of next: {self.bars[0]}')

    def post_next(self):
        if self._is_live:
            if self._trade_bot.is_order_updatable():
                self.update_active_order(is_instant_update=False)
            else:

                if self._trade_bot.active_order:
                    # TODO: implement unfilled pending order notification
                    raise Exception('There is a settled order in the trade has not been remove.\n'
                                    'It is required to remove the settled order before the next data refresh.\n'
                                    'Please check the order removal logic & procedure.')
                # else:
                #     pass
                #     print('There is no active order')

    def buy(self, is_market_buy: bool, ref_price=None, size=None, limit_price=None):

        if self._trade_bot.is_order_addable(isbuy=True):
            ref_price = ref_price if ref_price else self.bars[0]
            size = size if size is not None else self.getsizing(ref_price, isbuy=True)

            if size:
                if is_market_buy:
                    market_buy_order = Order(isbuy=OrderAction.BUY, order_type=OrderType.MARKET, size=size,
                                             trading_symbol=self._trading_symbol, ref_price=ref_price)

                    market_buy_order = self._broker.market_buy(order=market_buy_order)

                    self._trade_bot.add_order(market_buy_order)

                else:
                    if limit_price:
                        limit_buy_order = Order(isbuy=OrderAction.BUY, order_type=OrderType.LIMIT, size=size,
                                                trading_symbol=self._trading_symbol, ref_price=ref_price,
                                                limit_price=limit_price)

                        limit_buy_order = self._broker.limit_buy(order=limit_buy_order)

                        self._trade_bot.add_order(limit_buy_order)
                    else:
                        raise Exception('Limit order without limit price. Please provide limit price input')

    def sell(self, is_market_sell: bool, ref_price=None, size=None, limit_price=None):

        if self._trade_bot.is_order_addable(isbuy=False):
            ref_price = ref_price if ref_price else self.bars[0]
            size = size if size is not None else self.getsizing(ref_price, isbuy=True)

            if size:
                if is_market_sell:
                    market_sell_order = Order(isbuy=OrderAction.SELL, order_type=OrderType.MARKET, size=size,
                                              trading_symbol=self._trading_symbol, ref_price=ref_price)

                    market_sell_order = self._broker.market_sell(order=market_sell_order)

                    self._trade_bot.add_order(market_sell_order)

                else:
                    if limit_price:
                        limit_sell_order = Order(isbuy=OrderAction.SELL, order_type=OrderType.LIMIT, size=size,
                                                 trading_symbol=self._trading_symbol, ref_price=ref_price)

                        limit_sell_order = self._broker.limit_sell(order=limit_sell_order)
                        self._trade_bot.add_order(limit_sell_order)

                    else:
                        raise Exception('Limit order without limit price. Please provide limit price input')

    def update_active_order(self, is_instant_update: bool, next_refresh_ratio: float = 0.9, update_reps: int = 5):
        if self._is_live:
            order = self._trade_bot.active_order
            if is_instant_update:
                resp_order = self._broker.update_order_info(order)
                if resp_order.is_settled():
                    self._trade_bot.update_order(resp_order)
                    self.update_position()
                    # TODO: To implement notification
                elif resp_order.status != self._trade_bot.active_order.status:
                    self._trade_bot.update_order(resp_order)
                    print(f'There is a change in the active order status. The new status is {resp_order.status}')
                else:
                    print('There is no change in the active order')
            else:
                wait_duration = round(self._trade_bot.bar_time_gap * next_refresh_ratio)
                order_update_deadline = self._trade_bot.last_refresh_timestamp + wait_duration
                wait_time = math.floor(wait_duration / update_reps)

                update_count = 0
                while datetime.datetime.now().timestamp() < order_update_deadline and update_count <= update_reps:
                    time.sleep(wait_time)
                    resp_order = self._broker.update_order_info(order)

                    if resp_order.is_settled():
                        self._trade_bot.update_order(resp_order)
                        self.update_position()
                        # TODO: To implement notification
                        break
                    elif resp_order.status != self._trade_bot.active_order.status:
                        self._trade_bot.update_order(resp_order)
                        print(f'There is a change in the active order status. The new status is {resp_order.status}')
                    else:
                        print('There is no change in the active order')

                    update_count += 1

    def cancel_active_order(self):
        if not self._trade_bot.active_order.is_settled():
            self._trade_bot.active_order = self._broker.cancel_order(self._trade_bot.active_order)

    def update_position(self):
        self._position = self._broker.get_position(self._position)

    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order.status in [order.Completed]:
            if order.isbuy():
                print('BUY EXECUTED, Price: {0:8.2f}, Cost: {1:8.2f}, Comm: {2:8.2f}'.format(
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, {0:8.2f}, Cost: {1:8.2f}, Comm{2:8.2f}'.format(
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm))

            self.bar_executed = len(self)  # when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(
            trade.pnl, trade.pnlcomm))

    def notify_signal(self, trade):
        if not trade.isclosed:
            return
# class RSIStrategy(BaseStrategy):
#
#     def prepare(self):
#         self._bar_frame.add_fields(rsi=RSIIndicator(self._bar_frame.close, window=14, fillna=True).rsi())
#         self._bar_frame.add_fields(rsi_uphit_70=Indicator(self._bar_frame.frame['rsi']).is_up_hit(70))
#
#     def next(self):
#     #     print('bar 0:', self.bars[0])
#     #     print('bar -1:', self.bars[-1])
#         rsi = self.bars[0].rsi
#         price = self.bars[0].close
#         if rsi and self.bars[0].rsi_uphit_70 == 1:
#             # pass
#             print(f'RSI: {self.bars[0].rsi} and close price: {price}')
