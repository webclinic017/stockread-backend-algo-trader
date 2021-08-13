import datetime
import uuid
from abc import ABC
from enum import Enum
from typing import Optional


# DIVIDER: --------------------------------------
# INFO: OrderStatus Enum

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
                 client_ref_id, ticker_id=None):
        self.client_ref_id = client_ref_id
        self.trading_symbol = trading_symbol
        self.ticker_id = ticker_id
        self.ref_price = ref_price
        self.size = size
        self.isbuy = isbuy
        self.status = OrderStatus.CREATED
        self.created_at = datetime.datetime.now().isoformat()
        self.created_timestamp = datetime.datetime.now().timestamp()

        # order type to be defined by child classes
        self.ordtype: Optional[OrderType] = None

        # after-submit attributes
        self.broker_ref_id: Optional[str] = None
        self.is_broker_settled = None
        self.broker_traded_symbol = None

        # on-fill attributes
        self.filled_price: float = 0
        self.transaction_value: float = 0
        self.filled_at = None
        self.filled_timestamp = None
        self.fill_quantity: int = 0
        self.commission_fee: Optional[float] = None

    def __repr__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('TradingSymbol: {}'.format(self.trading_symbol))
        tojoin.append('OrderBrokerRefID: {}'.format(self.broker_ref_id))
        tojoin.append('OrderClientRefID: {}'.format(self.broker_ref_id))
        tojoin.append('OrderType: {}'.format(self.ordtype.value))
        tojoin.append('OrderAction: {}'.format('BUY' if self.isbuy else 'SELL'))
        tojoin.append('Status: {}'.format(self.status.value))
        tojoin.append('Size: {}'.format(self.size))
        tojoin.append('ReferencePrice: {}'.format(self.ref_price))
        tojoin.append('FilledPrice: {}'.format(self.filled_price))
        tojoin.append('FilledQuantity: {}'.format(self.fill_quantity))
        tojoin.append('IsSettledByBroker: {}'.format(self.is_broker_settled))
        tojoin.append('CreatedAt: {}'.format(self.created_at))
        tojoin.append('TransactionValue: {}'.format(self.transaction_value))

        return ', '.join(tojoin)

    @property
    def type(self):
        return str(self.ordtype.value).lower() if self.ordtype else 'UNDEFINED'

    def set_ticker_id(self, ticker_id):
        self.ticker_id = ticker_id

    def is_settled(self):
        """Returns True if the order is settled."""
        return self.status in [OrderStatus.CANCELED, OrderStatus.FILLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]

    def is_deactivated(self):
        """Returns True if the order is deactivated."""
        return self.status in [OrderStatus.CANCELED, OrderStatus.REJECTED, OrderStatus.EXPIRED]

    def is_submitted(self):
        """Returns True if the order state is OrderStatus.SUBMITTED."""
        return self.status == OrderStatus.SUBMITTED

    def is_canceled(self):
        """Returns True if the order state is OrderStatus.CANCELED."""
        return self.status == OrderStatus.CANCELED

    def is_filled(self):
        """Returns True if the order state is OrderStatus.FILLED."""
        return self.status == OrderStatus.FILLED

    def is_expired(self):
        """Returns True if the order state is OrderStatus.EXPIRED."""
        return self.status == OrderStatus.EXPIRED

    def is_market_order(self):
        """Returns True if the order tyoe is OrderType.MARKET."""
        return self.ordtype == OrderType.MARKET

    def is_limit_order(self):
        """Returns True if the order tyoe is OrderType.LIMIT."""
        return self.ordtype == OrderType.LIMIT

    def is_stop_order(self):
        """Returns True if the order tyoe is OrderType.STOP."""
        return self.ordtype == OrderType.STOP

    def is_stop_limit_order(self):
        """Returns True if the order tyoe is OrderType.STOP_LIMIT."""
        return self.ordtype == OrderType.STOP_LIMIT

# DIVIDER: --------------------------------------
# INFO: RegularOrder Concrete Class

class RegularOrder(BaseOrder):

    def __init__(self, trading_symbol: str, size: int, isbuy: bool,
                 islimit: bool, limit_price: float, client_ref_id=uuid.uuid1(),
                 ticker_id=None, ref_price=None):

        super().__init__(trading_symbol=trading_symbol, size=size, client_ref_id=client_ref_id,
                         isbuy=isbuy, ticker_id=ticker_id, ref_price=ref_price)

        self.islimit = islimit
        if self.islimit:
            self.limit_price = limit_price
            self.ordtype = OrderType.LIMIT
        else:
            self.ordtype = OrderType.MARKET

    def __str__(self):
        tojoin = list()
        tojoin.append('LimitPrice: {}'.format(self.limit_price))
        return self.__repr__() + ', ' + ', '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: StopOrder Concrete Class
class StopOrder(BaseOrder):

    def __init__(self, trading_symbol: str, size: int, isbuy: bool,
                 isstoplimit: bool, limit_price: float, stop_price: float, client_ref_id=uuid.uuid1(),
                 ticker_id=None, ref_price=None):

        super().__init__(trading_symbol=trading_symbol, size=size, client_ref_id=client_ref_id,
                         isbuy=isbuy, ticker_id=ticker_id, ref_price=ref_price)

        self.stop_price = stop_price
        self.isstoplimit = isstoplimit
        if self.isstoplimit:
            self.limit_price = limit_price
            self.ordtype = OrderType.STOP_LIMIT
        else:
            self.ordtype = OrderType.STOP

    def __str__(self):
        tojoin = list()
        tojoin.append('StopPrice: {}'.format(self.stop_price))
        tojoin.append('LimitPrice: {}'.format(self.limit_price))
        return self.__repr__() + ', ' + ', '.join(tojoin)

    def is_possibly_triggered(self, ref_price: float):
        if self.isbuy:
            return ref_price >= self.stop_price
        else:
            return ref_price <= self.stop_price


# DIVIDER: --------------------------------------
# INFO: Usage Examples
if __name__ == '__main__':
    sample_limit_order = RegularOrder('SHOP', size=10, isbuy=True, islimit=True, limit_price=1990.50,
                                      ref_price=1990.99)
    sample_stop_order = StopOrder('SHOP', size=10, isbuy=True, isstoplimit=True, limit_price=1990.50,
                                  stop_price=1990.50, ref_price=1990.99)
    print(sample_limit_order)
    print(sample_stop_order)
