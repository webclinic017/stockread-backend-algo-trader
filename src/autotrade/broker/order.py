import datetime
from enum import Enum
from typing import Optional


class OrderAction(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderStatus(Enum):
    CREATED = 'CREATED'  # BaseOrder has been created.
    SUBMITTED = 'SUBMITTED'  # BaseOrder has been submitted.
    ACCEPTED = 'ACCEPTED'  # BaseOrder has been acknowledged by the broker.
    CANCELED = 'CANCELED'  # BaseOrder has been canceled.
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'  # BaseOrder has been partially filled.
    FILLED = 'FILLED'  # BaseOrder has been completely filled.
    EXPIRED = 'EXPIRED'  # BaseOrder has been expired.
    REJECTED = 'REJECTED'  # BaseOrder has been rejected.

    NEW = 'NEW'  # BaseOrder has been created.
    PENDING = 'PENDING'  # BaseOrder has been created.
    OTHERS = 'OTHERS'  # BaseOrder has been created.


class OrderType(Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP_LIMIT = 'STOP_LIMIT'
    STOP = 'STOP'


class Order:

    def __init__(self, action: OrderAction, order_type: OrderType, size: int,
                 trading_symbol: str, ticker_id, limit_price=0, stop_price=0):
        self.ref_id: Optional[str] = None
        self.trading_symbol = trading_symbol
        self.ticker_id = ticker_id
        self.size = size
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.state = OrderStatus.CREATED
        self.is_broker_settled = None
        self.broker_traded_symbol = None
        self.type = order_type
        self.action = action
        self.created_at = datetime.datetime.now().isoformat()
        self.created_timestamp = datetime.datetime.utcnow().timestamp()
        self.filled_price: float = 0
        self.market_value: float = 0
        self.filled_at = None
        self.filled_timestamp = None
        self.fill_quantity: int = 0
        self.commission_fee: Optional[float] = None

    def __repr__(self):
        return 'Order({created_at} - {trading_symbol} >> {broker_traded_symbol}, ' \
               '{type}-{action}-{state}, ref_id: {ref_id}, size: {size}, filled price: {filled_price}, ' \
               'filled filled_quantity: {fill_quantity}, ' \
               'is_broker_settled: {is_broker_settled}, limit_price: {limit_price}, stop_price: {stop_price})'.format(
                created_at=self.created_at,
                trading_symbol=self.trading_symbol,
                broker_traded_symbol=self.broker_traded_symbol,
                type=self.type.value,
                action=self.action.value,
                state=self.state.value,
                ref_id=self.ref_id,
                size=self.size,
                filled_price=self.filled_price,
                fill_quantity=self.fill_quantity,
                is_broker_settled=self.is_broker_settled,
                limit_price=self.limit_price,
                stop_price=self.stop_price)

    def is_settled(self):
        """Returns True if the order is settled."""
        return self.state in [OrderStatus.CANCELED, OrderStatus.FILLED, OrderStatus.REJECTED]

    def is_submitted(self):
        """Returns True if the order state is OrderStatus.SUBMITTED."""
        return self.state == OrderStatus.SUBMITTED

    def is_canceled(self):
        """Returns True if the order state is OrderStatus.CANCELED."""
        return self.state == OrderStatus.CANCELED

    def is_filled(self):
        """Returns True if the order state is OrderStatus.FILLED."""
        return self.state == OrderStatus.FILLED

    def is_expired(self):
        """Returns True if the order state is OrderStatus.EXPIRED."""
        return self.state == OrderStatus.EXPIRED


if __name__ == '__main__':
    new_order = Order(action=OrderAction.BUY, order_type=OrderType.LIMIT, size=100,
                      trading_symbol="SHOP", ticker_id="sec-s-93a8e20409f34e01a053525c981f1ef1", limit_price=100)
    print(new_order)
