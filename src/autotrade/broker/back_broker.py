import datetime
import random
import string
import uuid
from typing import Union, Optional

from src.autotrade.artifacts.comm import Commission
from src.autotrade.artifacts.order import RegularOrder, OrderStatus, StopOrder
from src.autotrade.artifacts.position import Position
from src.autotrade.broker.base_broker import IBroker, BaseBroker
from src.errors import OrderTypeError, MissingPrice, UnmatchedTickerError, MissingRequiredTradingElement


# DIVIDER: --------------------------------------
# INFO: BackBroker Class

class BackBroker(BaseBroker, IBroker):

    def __init__(self, ask_bid_spread_floor: float = 0.0022, ask_bid_spread_ceiling: float = 0.0062,
                 lmt_fill_possibility: float = 0.85, slo_fill_possibility: float = 0.95,
                 comm: Commission = Commission()):

        super().__init__()
        self._is_live = False  # to modify the parent attribute to False for back_testing broker

        self._comm: Commission = comm

        # LIVE BROKER STIMULATION FACTORS
        self._half_ask_bid_spread_floor = ask_bid_spread_floor / 2
        self._half_ask_bid_spread_ceiling = ask_bid_spread_ceiling / 2
        self._lmt_fill_possibility = lmt_fill_possibility
        self._slo_fill_possibility = slo_fill_possibility

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    @property
    def is_live(self):
        return self._is_live

    @property
    def trading_symbol(self):
        if not self._trading_symbol:
            raise MissingRequiredTradingElement(element_type='trading_symbol')
        else:
            return self._trading_symbol

    @property
    def commission(self):
        return self._comm

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def initialize(self, trading_symbol: str, currency: str):
        """
        Initialize key attributes of the broker
        """
        self._trading_symbol = trading_symbol
        self._currency = currency
        self._find_ticker_id()
        self._position = Position(self._trading_symbol)
        self._position.set_ticker_id(ticker_id=self._ticker_id)
        self._position.set_currency(currency=self._currency)

    def _find_ticker_id(self):
        if not self._ticker_id:
            if not self._trading_symbol:
                raise MissingRequiredTradingElement('trading_symbol')
            else:
                self._ticker_id = self._trading_symbol
                return self._ticker_id

    def market_buy(self, order: RegularOrder) -> RegularOrder:
        """
        Places a market buy order for a security.
        """

        if order.islimit:
            raise OrderTypeError(expected_type='market', unexpected_type=order.type)

        elif not order.ref_price:
            raise MissingPrice(price_type='ref_price')

        else:
            return self._write_submitted_order(order)

    def market_sell(self, order: RegularOrder) -> RegularOrder:
        """
        Places a market sell order for a security.
        """
        if order.islimit:
            raise OrderTypeError(expected_type='market', unexpected_type=order.type)

        elif not order.ref_price:
            raise MissingPrice(price_type='ref_price')

        else:
            return self._write_submitted_order(order)

    def limit_buy(self, order: RegularOrder) -> RegularOrder:
        """
        Places a limit buy order for a security.
        """
        return self._write_submitted_order(order)

    def limit_sell(self, order: RegularOrder) -> RegularOrder:
        """
        Places a limit sell order for a security.
        """
        return self._write_submitted_order(order)

    def stop_limit_buy(self, order: StopOrder) -> StopOrder:
        """
        Places a stop limit buy order for a security.
        """
        if order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(expected_type='stop_limit', unexpected_type=order.type)

    def stop_limit_sell(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(expected_type='stop_limit', unexpected_type=order.type)

    def stop_loss(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if not order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(expected_type='stop', unexpected_type=order.type)

    def take_profit(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if not order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(expected_type='stop', unexpected_type=order.type)

    def cancel_order(self, order: Union[RegularOrder, StopOrder]) -> Union[RegularOrder, StopOrder]:
        """
        Cancel an order
        """
        if not order.is_settled():
            order._status = OrderStatus.CANCELED
            order._is_broker_settled = True

            # IMPORTANT: Upsert settled orders -> add to the broker's settled list and remove it from pending
            self._upsert_settled(order)

            return order

    def update_order(self, order: Union[RegularOrder, StopOrder],
                     ref_price: Optional[float] = None) -> Union[RegularOrder, StopOrder]:
        """
        Update an order if its status is still unsettled
        """

        if not self.is_live:
            if not ref_price:
                raise MissingPrice(price_type='ref_price')
        if order.is_stop_order() or order.is_stop_limit_order():
            if order.stop_price:

                if order.isstoplimit:  # stop limit order
                    if order.is_possibly_triggered(ref_price=ref_price):
                        return self._decide_if_lmt_get_filled(order, ref_price, self._slo_fill_possibility)
                else:  # stop order
                    if order.is_possibly_triggered(ref_price=ref_price):
                        market_price = self._randomize_market_price(ref_price, order.isbuy)
                        return self._write_filled_order(filled_price=market_price, order=order)

            else:
                raise MissingPrice(price_type='stop_price')

        else:
            if order.islimit:  # limit order
                return self._decide_if_lmt_get_filled(order, ref_price, self._slo_fill_possibility)
            else:  # market order
                market_price = self._randomize_market_price(order.ref_price, order.isbuy)
                return self._write_filled_order(filled_price=market_price, order=order)

    def update_pending_orders(self, ref_price: Optional[float] = None):
        if not self.is_live:
            if not ref_price:
                raise MissingPrice(price_type='ref_price')
            else:
                for _ord in list(self._pending_orders.values()):
                    self.update_order(_ord, ref_price)

    def get_position(self, is_live_position) -> Position:
        """
        Grabs the current BackTesting Trade position.
        """
        if not self.is_live:
            is_live_position = False

        if not is_live_position:
            return self._position

    # DIVIDER: Class Private Methods to Process Data Internally -----------------------------------

    def _randomize_market_price(self, ref_price: float, isbuy: bool):
        """TO SIMULATE REAL LIVE TRADE. It is to decide if a market order get filled at what price in a session
        (after submitting the order and before next data bar).
        The decision is based on the predefined ask_bid_spread floor & ceiling.
        """
        if isbuy:
            # buy at ask (higher than last filled price)

            return ref_price * (
                    1 + random.uniform(self._half_ask_bid_spread_floor, self._half_ask_bid_spread_ceiling))
        else:
            # sell at bid (lower than last filled price)
            return ref_price * (
                    1 - random.uniform(self._half_ask_bid_spread_floor, self._half_ask_bid_spread_ceiling))

    def _write_filled_order(self, filled_price: float,
                            order: Union[RegularOrder, StopOrder]) -> Union[RegularOrder, StopOrder]:
        """It is to assign values for in-common order attributes when the order get filled.
        IT IS REQUIRED THAT FILLED PRICE IS PROVIDED BEFORE RUNNING THIS METHOD
        """
        if self.trading_symbol == order.trading_symbol:
            if filled_price:
                order.set_filled_price(filled_price=filled_price)
                order.set_fill_quantity(fill_quantity=order.size)
                order.set_transaction_value(transaction_value=order.fill_quantity * order.filled_price)
                commission_fee = self.commission.estimate_commission(transaction_value=order.transaction_value)
                order.set_commission_fee(commission_fee=commission_fee)

                # generate information for filled order after
                order.set_status(status=OrderStatus.FILLED)
                order.set_filled_at(filled_at=datetime.datetime.now().isoformat())
                order.set_filled_timestamp(filled_timestamp=round(datetime.datetime.now().timestamp()))
                order.set_is_broker_settled(is_broker_settled=True)

                # IMPORTANT: Upsert settled orders -> add to the broker's settled list and remove it from pending
                self._upsert_settled(order)

                # IMPORTANT: Update position when order get filled
                self._position.update(order.isbuy, order.fill_quantity, order.filled_price)

            else:
                raise MissingPrice(price_type='filled_price')

        else:
            raise UnmatchedTickerError(primary_class_name=type(self).__name__,
                                       primary_class_ticker=self.trading_symbol,
                                       foreign_class_name=type(order).__name__,
                                       foreign_class_ticker=order.trading_symbol)
        return order

    def _decide_if_lmt_get_filled(self, order: Union[RegularOrder, StopOrder], ref_price: float,
                                  fill_possibility: float):
        """TO SIMULATE REAL LIVE TRADE. It is to decide if a limit order get filled in a session or not
        (after submitting the order and before next data bar).
        The decision is based on the predefined lmt_fill_possibility.
        """

        if not ref_price:
            raise MissingPrice(price_type='ref_price')

        filled_price = order.limit_price

        if order.is_limit_order():
            if not order.isbuy:
                if ref_price > filled_price:
                    # filled price has been provide before running this method
                    return self._write_filled_order(filled_price, order)

                elif ref_price == filled_price:
                    if random.uniform(0, 1) < fill_possibility:
                        # filled price has been provide before running this method
                        return self._write_filled_order(filled_price, order)

            else:
                if ref_price < filled_price:
                    # filled price has been provide before running this method
                    return self._write_filled_order(filled_price, order)

                elif ref_price == filled_price:
                    if random.uniform(0, 1) < fill_possibility:
                        # filled price has been provide before running this method
                        return self._write_filled_order(filled_price, order)

        elif order.is_stop_limit_order():
            return self._write_filled_order(filled_price, order)
        else:
            raise OrderTypeError(expected_type='limit', unexpected_type=order.type)

    def _write_submitted_order(self, order: Union[RegularOrder, StopOrder]):
        """It is to assign values for in-common order attributes when the order get submitted."""

        order.set_created_at(created_at=datetime.datetime.now().isoformat())
        order.set_created_timestamp(created_timestamp=round(datetime.datetime.now().timestamp()))
        order.set_status(status=OrderStatus.SUBMITTED)
        order.set_broker_ref_id(broker_ref_id=f"order-{uuid.uuid1().__str__()}-"
                                              f"{''.join(random.choice(string.ascii_lowercase) for i in range(10))}")
        order.set_ticker_id(ticker_id=self._ticker_id)
        order.set_is_broker_settled(is_broker_settled=False)
        order.set_broker_traded_symbol(broker_traded_symbol=order.trading_symbol)

        # IMPORTANT: Upsert pending orders -> add to the broker's pending order list
        self._upsert_pending(order)

        return order


# DIVIDER: --------------------------------------
# INFO: Usage Examples

if __name__ == '__main__':
    # pass
    back_broker = BackBroker()
    back_broker.initialize(trading_symbol='CGX', currency='CAD')
    print(back_broker.ticker_id)
    print(back_broker.position)

    market_buy_order = RegularOrder(isbuy=True, islimit=False, size=1, limit_price=10.05, trading_symbol='CGX',
                                    ref_price=10.20)

    limit_buy_order = RegularOrder(isbuy=True, islimit=True, size=1, limit_price=10.05, trading_symbol='CGX',
                                   ref_price=10.20)

    back_broker.market_buy(market_buy_order)
    back_broker.limit_buy(limit_buy_order)
    back_broker.update_pending_orders(ref_price=10.00)
    print(back_broker.pending_orders)
    print(back_broker.settled_orders)
