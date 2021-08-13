import datetime
import random
from typing import TYPE_CHECKING, Union

from src.autotrade.artifacts.comm import Commission
from src.autotrade.artifacts.order import RegularOrder, OrderStatus, StopOrder
from src.autotrade.artifacts.position import Position
from src.autotrade.broker.base_broker import IBroker, BaseBroker
from src.errors import OrderTypeError, MissingPrice, UnmatchedTickerError, MissingRequiredTradingElement

if TYPE_CHECKING:
    from src.autotrade.trade import Trade


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
    def ticker_symbol(self):
        if not self._trading_symbol:
            raise MissingRequiredTradingElement(class_name=type(self).__name__, element_type='trading_symbol')
        else:
            return self._trading_symbol

    # DIVIDER: Publicly Accessible Methods --------------------------------------------------------
    def bind_to_trade(self, trade: 'Trade'):
        """
        :type trade: Trade
        """
        self._trade = trade
        self._trading_symbol = self._trade.trading_symbol
        self._currency = self._trade.currency
        self._position = Position(self._trading_symbol)
        self._position.set_ticker_id(self._trading_symbol)
        self._position.set_currency(self._currency)

    def market_buy(self, order: RegularOrder) -> RegularOrder:
        """
        Places a market buy order for a security.
        """

        if order.islimit:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='market', unexpected_type=order.type)
        else:
            return self._write_submitted_order(order)

    def market_sell(self, order: RegularOrder) -> RegularOrder:
        """
        Places a market sell order for a security.
        """
        if order.islimit:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='market', unexpected_type=order.type)
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
            raise OrderTypeError(class_name=type(self).__name__, expected_type='stop_limit', unexpected_type=order.type)

    def stop_limit_sell(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='stop_limit', unexpected_type=order.type)

    def stop_loss(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if not order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='stop', unexpected_type=order.type)

    def take_profit(self, order: StopOrder) -> StopOrder:
        """
        Places a limit sell order for a security.
        """
        if not order.isstoplimit:
            return self._write_submitted_order(order)
        else:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='stop', unexpected_type=order.type)

    def cancel_order(self, order: RegularOrder) -> RegularOrder:
        """
        Cancel an order
        """
        if not order.is_settled():
            order.status = OrderStatus.CANCELED
            order.is_broker_settled = True

            # IMPORTANT: Upsert settled orders -> add to the broker's settled list and remove it from pending
            self._upsert_settled(order)

            return order

    def update_order(self, order: Union[RegularOrder, StopOrder], ref_price: float):
        """
        Cancel an order from its submitted state
        """
        if order.is_stop_order() or order.is_stop_limit_order():
            if order.stop_price:
                if ref_price:
                    if order.isstoplimit:  # stop limit order
                        if order.is_possibly_triggered(ref_price=ref_price):
                            return self._decide_if_lmt_get_filled(order, ref_price, self._slo_fill_possibility)
                    else:  # stop order
                        if order.is_possibly_triggered(ref_price=ref_price):
                            market_price = self._randomize_market_price(ref_price, order.isbuy)
                            return self._write_filled_order(filled_price=market_price, order=order)
                else:
                    raise MissingPrice(class_name=type(self).__name__, price_type='ref_price')

            else:
                raise MissingPrice(class_name=type(self).__name__, price_type='stop_price')

        else:
            if order.is_limit_order():  # limit order
                if ref_price:
                    return self._decide_if_lmt_get_filled(order, ref_price, self._slo_fill_possibility)
                else:
                    raise MissingPrice(class_name=type(self).__name__, price_type='ref_price')

            else:  # market order
                market_price = self._randomize_market_price(order.ref_price, order.isbuy)
                return self._write_filled_order(filled_price=market_price, order=order)

    def update_pending_orders(self, ref_price: float):
        if not ref_price:
            raise MissingPrice(class_name=type(self).__name__, price_type='ref_price')
        else:
            for _ord in self._pending_orders.values():
                self.update_order(_ord, ref_price)

    def get_position(self, position: Position, is_live_position) -> Position:
        """
        Grabs the current BackTesting Trade position.
        """
        if not self.is_live:
            is_live_position = False

        if not is_live_position:
            if self._position.ticker_symbol == position.ticker_symbol:
                return self._position
            else:
                raise UnmatchedTickerError(primary_class_name=type(self).__name__,
                                           primary_class_ticker=self._position.ticker_symbol,
                                           foreign_class_name=type(position).__name__,
                                           foreign_class_ticker=position.ticker_symbol)

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

    def _write_filled_order(self, filled_price: float, order: Union[RegularOrder, StopOrder]) -> RegularOrder:
        """It is to assign values for in-common order attributes when the order get filled.
        IT IS REQUIRED THAT FILLED PRICE IS PROVIDED BEFORE RUNNING THIS METHOD
        """
        if self._trading_symbol == order.trading_symbol:
            if filled_price:
                order.filled_price = filled_price
                order.fill_quantity = order.size
                order.transaction_value = order.fill_quantity * order.filled_price
                order.commission_fee = self._comm.estimate_commission(transaction_value=order.transaction_value)

                # generate information for filled order after
                order.status = OrderStatus.FILLED
                order.filled_at = datetime.datetime.now().isoformat()
                order.filled_timestamp = datetime.datetime.now().timestamp()
                order.is_broker_settled = True

                # IMPORTANT: Upsert settled orders -> add to the broker's settled list and remove it from pending
                self._upsert_settled(order)

                # IMPORTANT: Update position when order get filled
                self._position.update(order.isbuy, order.fill_quantity, order.filled_price)

            else:
                raise MissingPrice(class_name=type(self).__name__, price_type='filled_price')

        else:
            raise UnmatchedTickerError(primary_class_name=type(self).__name__,
                                       primary_class_ticker=self._trading_symbol,
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
            raise MissingPrice(class_name=type(self).__name__, price_type='ref_price')

        if order.islimit or order.isstoplimit:
            filled_price = order.limit_price

            if ref_price > filled_price:
                # filled price has been provide before running this method
                return self._write_filled_order(filled_price, order)

            elif ref_price == filled_price:
                if random.uniform(0, 1) < fill_possibility:
                    # filled price has been provide before running this method
                    return self._write_filled_order(filled_price, order)

        else:
            raise OrderTypeError(class_name=type(self).__name__, expected_type='limit', unexpected_type=order.type)

    def _write_submitted_order(self, order: Union[RegularOrder, StopOrder]):
        """It is to assign values for in-common order attributes when the order get submitted."""

        order.status = OrderStatus.SUBMITTED

        order.broker_ref_id = order.client_ref_id
        order.set_ticker_id(self._trading_symbol)
        order.is_broker_settled = False
        order.broker_traded_symbol = order.trading_symbol

        # IMPORTANT: Upsert pending orders -> add to the broker's pending order list
        self._upsert_pending(order)

        return order
