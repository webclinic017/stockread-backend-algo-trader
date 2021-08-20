import datetime
import math
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union, Dict, Deque

from src.autotrade.artifacts.order import RegularOrder, StopOrder
from src.autotrade.bars.bar import Bar
from src.autotrade.bars.barfeed import BarFeed
from src.autotrade.signal.signal import Signal
from src.errors import MissingPrice, UnsettledOrderPersistError, MultiplePendingOrderException

# Typing without cyclic imports
if TYPE_CHECKING:
    from src.autotrade.trade import Trade


# DIVIDER: --------------------------------------
# INFO: BaseStrategy Abstract Class (Strategy - BaseClass)

class BaseStrategy(ABC):

    def __init__(self):
        # set from Trade class
        self._trade: Optional['Trade'] = None
        self._submitted_orders: Dict[str, Union[RegularOrder, StopOrder]] = dict()

        # BARS & BARS CONTROL
        self._barfeed: Optional[BarFeed] = None
        self._bars: Optional[Deque[Bar]] = None
        self._last_bar_timestamp = None
        self._next_bar_timestamp = None
        self._bar_count = 0

    # DIVIDER: Required Class Construction Methods --------------------------------------------------------

    def __iter__(self):
        return self

    def __next__(self):
        self.setup()
        self.pre_next()
        self.print_bar()
        self.next()
        self.post_next()

    def bind_to_trade(self, trade: 'Trade'):
        self._trade = trade

        # TODO: (1): add TrailingController instance (if required else)
        # TODO: (2): add logging and notify (notification)
        # TODO: (3): method prepare (setup) pretrade ... to setup trailing and indicator and signal
        # TODO: (4): next to run and update bars for live trading, test again real data
        # TODO: (5): implement notify signal method

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------

    @property
    def submitted_orders(self):
        return self._submitted_orders

    @property
    def trade(self):
        return self._trade

    @property
    def trading_symbol(self):
        return self.trade.trading_symbol

    @property
    def position(self):
        return self.trade.broker.get_position(is_live_position=False)

    @property
    def broker(self):
        return self.trade.broker

    @property
    def sizer(self):
        return self.trade.sizer

    @property
    def stp_pricer(self):
        return self.trade.stp_pricer

    @property
    def barfeed(self):
        if self._last_bar_timestamp != self.trade.barfeed.last_bar.timestamp:
            self._barfeed = self.trade.barfeed
            self._last_bar_timestamp = self.trade.barfeed.latest_bar.timestamp
        return self._barfeed

    @property
    def gl_tracker(self):
        return self.trade.gl_tracker

    @property
    def is_live(self):
        return self.trade.is_live_trade

    @property
    def bar_time_gap(self):
        return self.trade.bar_time_gap

    @property
    def last_refresh_timestamp(self):
        return self.trade.last_refresh_timestamp

    @property
    def bars(self):
        return self._bars

    @property
    def filled_orders(self):
        if self.broker.settled_orders:
            return {order.broker_ref_id: order for order in self.broker.settled_orders.values() if order.is_filled()}

    @property
    def pending_stop_order(self):
        if self.broker.pending_orders:
            pending_stp = [order for order in self.broker.pending_orders.values() if
                           order.is_stop_order() or order.is_stop_limit_order()]
            if len(pending_stp) > 1:
                raise MultiplePendingOrderException(pending_orders=pending_stp, is_regular_order=False)
            else:
                if pending_stp:
                    return pending_stp[0]

    @property
    def pending_regular_order(self):

        if self.broker.pending_orders:
            pending_reg_odr = [order for order in self.broker.pending_orders.values()
                               if order.is_market_order() or order.is_limit_order()]

            if len(pending_reg_odr) > 1:
                raise MultiplePendingOrderException(pending_orders=pending_reg_odr, is_regular_order=True)
            else:
                if pending_reg_odr:
                    return pending_reg_odr[0]

    @property
    def buy_count(self):
        if self.broker.settled_orders:
            return len([_ord for _ord in self.broker.settled_orders.values() if _ord.isbuy and _ord.is_filled()])
        else:
            return 0

    @property
    def sell_count(self):
        if self.broker.settled_orders:
            return len([_ord for _ord in self.broker.settled_orders.values() if not _ord.isbuy and _ord.is_filled()])
        else:
            return 0

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------

    # INFO: Strategy Preparation & Setup
    @abstractmethod
    def prepare(self):
        raise NotImplementedError()

    @abstractmethod
    def print_bar(self):
        raise NotImplementedError()

    # INFO: Data Interval Management & Dealing with Bars
    def pre_next(self):
        if self.pending_regular_order:
            self.update_pending_orders(is_multiple_update=False)

        if self.pending_regular_order:
            self.cancel_order(self.pending_regular_order)
            time.sleep(
                5 if self.is_live else 0)  # wait 5 seconds (or some time) for cancelling request to be processed by the broker
            self.update_pending_orders(is_multiple_update=False)

        if self.pending_regular_order:
            raise UnsettledOrderPersistError(order=self.pending_regular_order)

    @abstractmethod
    def next(self):
        raise NotImplementedError()

    def post_next(self):
        # print(f'is live: {self.is_live}')
        if self.is_live:
            update_times = (self.bar_time_gap / 60) + 1
            self.update_pending_orders(is_multiple_update=True, update_reps=update_times)

        else:
            self.update_pending_orders(is_multiple_update=False)

    # INFO: Trade & Order Monitoring
    def buy(self, islimit: bool, ref_price: float = 0.0, size=None, limit_price=None):
        ref_price = ref_price if ref_price else self.bars[0].close

        # IMPORTANT: Check conditions before placing an order
        if self.pending_regular_order:
            return

        # print(f'limit: {self.trade.reps_limit}')
        # print(f'count: {self.buy_count}')

        if self.trade.reps_limit <= self.buy_count:
            return

        size = size if size is not None else self._getsizing(isbuy=True, ref_price=ref_price)

        if size:
            if islimit:
                if limit_price:
                    limit_buy_order = RegularOrder(isbuy=True, islimit=islimit, size=size, limit_price=limit_price,
                                                   trading_symbol=self.trading_symbol, ref_price=ref_price)

                    submitted_order = self.broker.limit_buy(order=limit_buy_order)

                else:
                    raise MissingPrice(price_type='limit_price')

            else:
                market_buy_order = RegularOrder(isbuy=True, islimit=islimit, size=size, limit_price=limit_price,
                                                trading_symbol=self.trading_symbol, ref_price=ref_price)

                submitted_order = self.broker.market_buy(order=market_buy_order)

            self._submitted_orders[submitted_order.broker_ref_id] = submitted_order
            self.notify_order(order=submitted_order)

    def sell(self, islimit: bool, ref_price=None, size=None, limit_price=None):

        # IMPORTANT: Check conditions before placing an order
        if self.pending_regular_order:
            return

        if self.trade.reps_limit <= self.sell_count:
            return

        for _ in range(3):
            if self.pending_stop_order:
                self.cancel_order(order=self.pending_stop_order)
                time.sleep(3 if self.is_live else 0)
                self.update_pending_orders(is_multiple_update=False)
            else:
                break

        ref_price = ref_price if ref_price else self.bars[0].close
        size = size if size is not None else self._getsizing(isbuy=False, ref_price=ref_price)

        if size:
            if islimit:
                if limit_price:
                    limit_sell_order = RegularOrder(isbuy=False, islimit=islimit, size=size,
                                                    limit_price=limit_price,
                                                    trading_symbol=self.trading_symbol, ref_price=ref_price)

                    submitted_order = self.broker.limit_sell(order=limit_sell_order)
                else:
                    raise MissingPrice(price_type='limit_price')

            else:
                market_sell_order = RegularOrder(isbuy=False, islimit=islimit, size=size, limit_price=limit_price,
                                                 trading_symbol=self.trading_symbol, ref_price=ref_price)

                submitted_order = self.broker.market_sell(order=market_sell_order)

            self._submitted_orders[submitted_order.broker_ref_id] = submitted_order
            self.notify_order(order=submitted_order)

    def stoploss(self, isstoplimit: bool, stop_price: float, ref_price=None, size=None, limit_price=None):

        # IMPORTANT: Check conditions before placing an order
        if self.pending_stop_order:
            return

        if self.trade.reps_limit <= self.sell_count:
            return

        ref_price = ref_price if ref_price else self.bars[0].close
        size = size if size is not None else self._getsizing(isbuy=False, ref_price=ref_price)

        if not stop_price:
            raise MissingPrice(price_type='stop_price')

        if size:
            if isstoplimit:
                if limit_price:
                    stop_limit_order = StopOrder(isbuy=False, size=size, isstoplimit=isstoplimit,
                                                 stop_price=stop_price, limit_price=limit_price, ref_price=ref_price,
                                                 trading_symbol=self.trading_symbol)

                    submitted_stp = self.broker.stop_limit_sell(order=stop_limit_order)
                else:
                    raise MissingPrice(price_type='limit_price')

            else:
                stop_order = StopOrder(isbuy=False, size=size, isstoplimit=isstoplimit,
                                       stop_price=stop_price, limit_price=limit_price, ref_price=ref_price,
                                       trading_symbol=self.trading_symbol)

                submitted_stp = self.broker.stop_loss(order=stop_order)

            self._submitted_orders[submitted_stp.broker_ref_id] = submitted_stp
            self.notify_order(order=submitted_stp)

    def update_pending_orders(self, is_multiple_update: bool, ref_price: float = 0.0,
                              next_refresh_ratio: float = 0.9, update_reps: int = 5):

        ref_price = ref_price if ref_price else self.bars[0].close

        if self.broker.pending_orders:

            if is_multiple_update:

                wait_duration = round(self.bar_time_gap * next_refresh_ratio)
                order_update_deadline = self.last_refresh_timestamp + wait_duration
                wait_time = math.floor(wait_duration / update_reps)

                update_count = 0
                while datetime.datetime.now().timestamp() < order_update_deadline and update_count <= update_reps:
                    time.sleep(wait_time)
                    self.broker.update_pending_orders(ref_price=ref_price)
                    self.monitor_and_notify()
                    if not self.pending_regular_order:
                        return
                    update_count += 1

            else:
                self.broker.update_pending_orders(ref_price=ref_price)
                self.monitor_and_notify()

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------

    def monitor_and_notify(self, ref_price: float = 0.0):
        ref_price = ref_price if ref_price else self.bars[0].close

        for _ord_id in list(self.submitted_orders.keys()):
            if _ord_id in self.broker.settled_orders:
                settled_order = self.broker.settled_orders[_ord_id]
                self.notify_order(order=settled_order)
                self._submitted_orders.pop(_ord_id)
                if settled_order.is_filled():
                    if settled_order.isbuy:
                        self.gl_tracker.add_holding(purchase_value=settled_order.transaction_value,
                                                    purchase_volume=settled_order.fill_quantity)

                    else:
                        self.gl_tracker.make_sale(sale_value=settled_order.transaction_value,
                                                  sale_volume=settled_order.fill_quantity)

                    if settled_order.is_stop_order() or settled_order.is_stop_limit_order():
                        self.stp_pricer.reset_trailing()

                    self.notify_trade(ref_price=ref_price)
                    if self.sell_count == self.buy_count == self.trade.reps_limit:
                        self.trade.close_trade()
                        print('The trade has been completed and closed')

    def cancel_order(self, order: Union[RegularOrder, StopOrder]):
        submitted_order = self.broker.cancel_order(order)
        self._submitted_orders[submitted_order.broker_ref_id] = submitted_order

    def cancel_orders(self):
        if self.broker.pending_orders:
            for _ord in list(self.broker.pending_orders.values()):
                submitted_order = self.broker.cancel_order(_ord)
                self._submitted_orders[submitted_order.broker_ref_id] = submitted_order

    def trail_stoploss(self, isstoplimit: Optional[bool] = True, stop_price: float = 0.0, limit_price: float = 0.0,
                       ref_price: float = 0.0):

        if not self.pending_stop_order:
            return

        ref_price = ref_price if ref_price else self.bars[0].close

        if not stop_price:
            # print(f'current ref price {ref_price} vs stop lastest ref_price {self.stp_pricer.latest_ref_price} vs stop price {self.stp_pricer.latest_stop_price}')
            price_dict = self.stp_pricer.get_stop_limit_prices(ref_price=ref_price)
            # print(price_dict)
            if price_dict:
                stop_price = price_dict['stop_price']
                limit_price = price_dict['limit_price']
            else:
                return
        else:
            if not limit_price:
                limit_price = stop_price

        # cancel current stoploss before placing new one
        for _ in range(3):
            if self.pending_stop_order:
                self.cancel_order(order=self.pending_stop_order)
                time.sleep(3 if self.is_live else 0)
                self.update_pending_orders(is_multiple_update=False)
            else:
                break

        if self.pending_stop_order:
            raise Exception('Unable to cancel the current pending stop order')

        self.stoploss(isstoplimit=isstoplimit, stop_price=stop_price, limit_price=limit_price, ref_price=ref_price)

    def notify_order(self, order: Union[RegularOrder, StopOrder]):
        # 1. If order is submitted do nothing
        if not order.is_settled():
            print(f'An order has been {order.status}.\n'
                  f'Order details: {order}')

        # 2. If order is buy/sell executed, report price executed
        elif order.is_filled():
            if order.isbuy:
                print(f'BUY EXECUTED, Price: {order.filled_price}, Cost: {order.transaction_value}, '
                      f'Quantity: {order.fill_quantity}, Comm: {order.commission_fee}.\n'
                      f'BUY COUNT {self.buy_count}/{self.trade.reps_limit}.\n'
                      f'Order details: {order}')
            else:
                print(f'SELL EXECUTED, Price: {order.filled_price}, Revenue: {order.transaction_value}, '
                      f'Quantity: {order.fill_quantity}, Comm: {order.commission_fee}.\n'
                      f'SELL COUNT {self.sell_count}/{self.trade.reps_limit}\n'
                      f'Order details: {order}')

        # 3. If order is canceled/margin/rejected, report order canceled
        else:
            print(f'An order has been {order.status}.\n'
                  f'Order details: {order}')

    def notify_trade(self, ref_price: float = 0.0):
        ref_price = ref_price if ref_price else self.bars[0].close

        realized = self.gl_tracker.realized_gain_loss
        unrealized = self.gl_tracker.estimate_unrealized_gls(market_price=ref_price)
        if realized > 0:
            realized_text = 'GAIN'
        else:
            realized_text = 'LOSS'

        if unrealized > 0:
            unrealized_text = 'GAIN'
        else:
            unrealized_text = 'LOSS'

        print(f'OPERATION REALIZED {realized_text} of {realized} and UNREALIZED {unrealized_text} of {unrealized}')

    def notify_signal(self, signal: Signal):
        if signal.is_up:
            print(f'{signal.sequence.upper()} {"BUY" if signal.isbuy else "SELL"} SIGNAL IS UP, '
                  f'Sequential: {signal.sequential}, DateTime: {signal.signal_up_datetime}, '
                  f'Codename: {signal.codename}, PriceAtSignal: {signal.price_at_signal}, '
                  f'IndicatorValueAtSignal: {signal.indicator_value_at_signal}, Notes: '
                  f'{signal.notes}.\n'
                  f'PENDING ORDER: {self.pending_regular_order}\n'
                  f'POSITION: {self.position}')

    def setup(self):
        # IMPORTANT: This line helps to avoid AttributeError: 'NoneType' of barfeed - when running prepare() method
        if not self._last_bar_timestamp:
            self._barfeed = self.trade.barfeed

        self.prepare()
        self._bars = next(self.barfeed)

    def _getsizing(self, isbuy=True, ref_price=None):
        # TODO: (1): Implement isbuy check for False
        # TODO: (2): Implement isbuy check for ref_price (if broker buy_power sufficient)
        ref_price = ref_price if ref_price else self.bars[0].close

        if isbuy:
            if self.sizer.isbysize:
                return self.sizer.size
            else:
                return self.sizer.sizebyamount(ref_price=ref_price)

        else:
            if self.sizer.isbysize:
                return self.sizer.size
            else:
                return self.position.size
