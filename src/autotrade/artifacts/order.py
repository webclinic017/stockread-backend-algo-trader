# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com
import random
import string
import uuid
from abc import ABC
from enum import Enum
from typing import Optional

# DIVIDER: --------------------------------------
# INFO: OrderStatus Enum
from src.errors import MissingOrderAttributeError


class OrderStatus(Enum):
    CREATED = 'CREATED'  # BaseOrder has been created at the trader end.
    SUBMITTED = 'SUBMITTED'  # BaseOrder has been submitted.
    ACCEPTED = 'ACCEPTED'  # BaseOrder has been acknowledged by the broker.
    CANCELED = 'CANCELED'  # BaseOrder has been canceled.
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'  # BaseOrder has been partially filled.
    FILLED = 'FILLED'  # BaseOrder has been completely filled.
    EXPIRED = 'EXPIRED'  # BaseOrder has been expired.
    REJECTED = 'REJECTED'  # BaseOrder has been rejected.

    NEW = 'NEW'  # BaseOrder has been created at the broker end.
    PENDING = 'PENDING'
    OTHERS = 'OTHERS'


# DIVIDER: --------------------------------------
# INFO: OrderType Enum

class OrderType(Enum):
    MARKET = 'MARKET'  # Abbreviation: MKT (mkt)
    LIMIT = 'LIMIT'  # Abbreviation: LMT (lmt)
    STOP_LIMIT = 'STOP_LIMIT'  # Abbreviation: SLO (slo)
    STOP = 'STOP'  # Abbreviation: STP (stp)


# DIVIDER: --------------------------------------
# INFO: BaseOrder Abstract Class

class BaseOrder(ABC):
    def __init__(self, trading_symbol: str, size: int, isbuy: bool, ref_price: float,
                 client_ref_id):
        self._client_ref_id = client_ref_id
        self._trading_symbol = trading_symbol
        self._ref_price = ref_price
        self._size = size
        self._isbuy = isbuy

        self._status = OrderStatus.CREATED

        # order type to be defined by child classes
        self._order_type: Optional[OrderType] = None

        # pre-submit attributes
        self._ticker_id: Optional[str] = None  # get ticker_id from broker

        # after-submit attributes
        self._created_at: Optional[str] = None
        self._created_timestamp: Optional[int] = None
        self._broker_ref_id: Optional[str] = None
        self._is_broker_settled: Optional[bool] = None
        self._broker_traded_symbol: Optional[str] = None

        # on-fill attributes
        self._filled_price: float = 0.0
        self._transaction_value: float = 0.0
        self._filled_at = None
        self._filled_timestamp = None
        self._fill_quantity: int = 0
        self._commission_fee: float = 0.0

    def __repr__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('TradingSymbol: {}'.format(self._trading_symbol))
        tojoin.append('OrderType: {}'.format(self._order_type.value))
        tojoin.append('OrderAction: {}'.format('BUY' if self._isbuy else 'SELL'))
        tojoin.append('Status: {}'.format(self._status.value))
        tojoin.append('Size: {}'.format(self._size))
        tojoin.append('ReferencePrice: {}'.format(self._ref_price))
        tojoin.append('FilledPrice: {}'.format(self._filled_price))
        tojoin.append('FilledQuantity: {}'.format(self._fill_quantity))
        tojoin.append('OrderClientRefID: {}'.format(self._client_ref_id))
        tojoin.append('OrderBrokerRefID: {}'.format(self._broker_ref_id))
        tojoin.append('IsSettledByBroker: {}'.format(self._is_broker_settled))
        tojoin.append('CreatedAt: {}'.format(self._created_at))
        tojoin.append('TransactionValue: {}'.format(self._transaction_value))

        return ', '.join(tojoin)

    # DIVIDER: Publicly Accessible Method Properties ----------------------------------------------
    # INFO: Class Getters
    @property
    def size(self):
        return self._size

    @property
    def isbuy(self):
        return self._isbuy

    @property
    def ref_price(self):
        if not self._ref_price:
            raise MissingOrderAttributeError(attribute='ref_price')
        return self._ref_price

    @property
    def client_ref_id(self):
        return self._client_ref_id

    @property
    def trading_symbol(self):
        return self._trading_symbol

    @property
    def status(self):
        return str(self._status.value).lower()

    @property
    def type(self):
        return str(self._order_type.value).lower() if self._order_type else 'undefined'

    @property
    def ticker_id(self):
        if not self._ticker_id:
            raise MissingOrderAttributeError(attribute='ticker_id')
        return self._ticker_id

    # after-submit attributes
    @property
    def created_at(self):
        return self._created_at

    @property
    def created_timestamp(self):
        return self._created_timestamp

    @property
    def broker_ref_id(self):
        if not self._broker_ref_id:
            raise MissingOrderAttributeError(attribute='broker_ref_id')
        return self._broker_ref_id

    @property
    def is_broker_settled(self):
        if self._is_broker_settled is None:
            raise MissingOrderAttributeError(attribute='is_broker_settled')
        return self._is_broker_settled

    @property
    def broker_traded_symbol(self):
        if not self._broker_traded_symbol:
            raise MissingOrderAttributeError(attribute='broker_traded_symbol')
        return self._broker_traded_symbol

    # on-fill attributes
    @property
    def filled_price(self):
        return self._filled_price

    @property
    def transaction_value(self):
        return self._transaction_value

    @property
    def filled_at(self):
        if not self._filled_at:
            raise MissingOrderAttributeError(attribute='filled_at')
        return self._filled_at

    @property
    def filled_timestamp(self):
        if not self._filled_timestamp:
            raise MissingOrderAttributeError(attribute='filled_timestamp')
        return self._filled_timestamp

    @property
    def fill_quantity(self):
        return self._fill_quantity

    @property
    def commission_fee(self):
        return self._commission_fee

    # INFO: Class Setters

    # after-submit attributes
    def set_ticker_id(self, ticker_id: str):
        self._ticker_id = ticker_id

    def set_created_at(self, created_at: str):
        self._created_at = created_at

    def set_created_timestamp(self, created_timestamp: int):
        self._created_timestamp = created_timestamp

    def set_broker_ref_id(self, broker_ref_id: str):
        self._broker_ref_id = broker_ref_id

    def set_is_broker_settled(self, is_broker_settled: bool):
        self._is_broker_settled = is_broker_settled

    def set_broker_traded_symbol(self, broker_traded_symbol: str):
        self._broker_traded_symbol = broker_traded_symbol

    def set_status(self, status: OrderStatus):
        self._status = status

    # on-fill attributes
    def set_filled_price(self, filled_price: float):
        self._filled_price = filled_price

    def set_transaction_value(self, transaction_value: float):
        self._transaction_value = transaction_value

    def set_filled_at(self, filled_at: str):
        self._filled_at = filled_at

    def set_filled_timestamp(self, filled_timestamp: int):
        self._filled_timestamp = filled_timestamp

    def set_fill_quantity(self, fill_quantity: int):
        self._fill_quantity = fill_quantity

    def set_commission_fee(self, commission_fee: float):
        self._commission_fee = commission_fee

    def is_settled(self):
        """Returns True if the order is settled."""
        return self._status in [OrderStatus.CANCELED, OrderStatus.FILLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]

    def is_deactivated(self):
        """Returns True if the order is deactivated."""
        return self._status in [OrderStatus.CANCELED, OrderStatus.REJECTED, OrderStatus.EXPIRED]

    def is_submitted(self):
        """Returns True if the order state is OrderStatus.SUBMITTED."""
        return self._status == OrderStatus.SUBMITTED

    def is_canceled(self):
        """Returns True if the order state is OrderStatus.CANCELED."""
        return self._status == OrderStatus.CANCELED

    def is_filled(self):
        """Returns True if the order state is OrderStatus.FILLED."""
        return self._status == OrderStatus.FILLED

    def is_expired(self):
        """Returns True if the order state is OrderStatus.EXPIRED."""
        return self._status == OrderStatus.EXPIRED

    def is_market_order(self):
        """Returns True if the order tyoe is OrderType.MARKET."""
        return self._order_type == OrderType.MARKET

    def is_limit_order(self):
        """Returns True if the order tyoe is OrderType.LIMIT."""
        return self._order_type == OrderType.LIMIT

    def is_stop_order(self):
        """Returns True if the order tyoe is OrderType.STOP."""
        return self._order_type == OrderType.STOP

    def is_stop_limit_order(self):
        """Returns True if the order tyoe is OrderType.STOP_LIMIT."""
        return self._order_type == OrderType.STOP_LIMIT


# DIVIDER: --------------------------------------
# INFO: RegularOrder Concrete Class

class RegularOrder(BaseOrder):

    def __init__(self, trading_symbol: str, size: int, isbuy: bool, islimit: bool, limit_price: float,
                 client_ref_id=f"c-order-{uuid.uuid1().__str__()}-"
                               f"{''.join(random.choice(string.ascii_lowercase) for _ in range(10))}", ref_price=None):

        super().__init__(trading_symbol=trading_symbol, size=size, client_ref_id=client_ref_id,
                         isbuy=isbuy, ref_price=ref_price)

        self._islimit = islimit
        if self._islimit:
            self._limit_price = limit_price
            self._order_type = OrderType.LIMIT
        else:
            self._order_type = OrderType.MARKET

    def __str__(self):
        tojoin = list()
        tojoin.append('LimitPrice: {}'.format(self._islimit))
        return self.__repr__() + ', ' + ', '.join(tojoin)

    @property
    def islimit(self):
        return self._islimit

    @property
    def limit_price(self):
        return self._limit_price


# DIVIDER: --------------------------------------
# INFO: StopOrder Concrete Class
class StopOrder(BaseOrder):

    def __init__(self, trading_symbol: str, size: int, isbuy: bool,
                 isstoplimit: bool, limit_price: float, stop_price: float,
                 client_ref_id=f"c-stp-order-{uuid.uuid1().__str__()}-"
                               f"{''.join(random.choice(string.ascii_lowercase) for _ in range(10))}", ref_price=None):

        super().__init__(trading_symbol=trading_symbol, size=size, client_ref_id=client_ref_id,
                         isbuy=isbuy, ref_price=ref_price)

        self._stop_price = stop_price
        self._isstoplimit = isstoplimit
        if self._isstoplimit:
            self._limit_price = limit_price
            self._order_type = OrderType.STOP_LIMIT
        else:
            self._order_type = OrderType.STOP

    def __str__(self):
        tojoin = list()
        tojoin.append('StopPrice: {}'.format(self._stop_price))
        tojoin.append('LimitPrice: {}'.format(self._limit_price))
        return self.__repr__() + ', ' + ', '.join(tojoin)

    def is_possibly_triggered(self, ref_price: float):
        if not self._isbuy:
            return ref_price <= self._stop_price
        else:
            return ref_price >= self._stop_price

    @property
    def limit_price(self):
        return self._limit_price

    @property
    def isstoplimit(self):
        return self._isstoplimit

    @property
    def stop_price(self):
        return self._limit_price


# DIVIDER: --------------------------------------
# INFO: Usage Examples
if __name__ == '__main__':
    sample_limit_order = RegularOrder('SHOP', size=10, isbuy=True, islimit=True, limit_price=1990.50,
                                      ref_price=1990.99)
    sample_stop_order = StopOrder('SHOP', size=10, isbuy=True, isstoplimit=True, limit_price=1990.50,
                                  stop_price=1990.50, ref_price=1990.99)
    print(sample_limit_order)
    print(sample_stop_order)
