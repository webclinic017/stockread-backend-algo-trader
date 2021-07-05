from enum import Enum


class OrderType(Enum):
    BUY = 1
    SELL = 2
    ALL = 3


class Order:
    def __init__(self, result: dict):
        self.order_id = result['order_id']
        self.symbol = result['symbol']
        self.security_id = result['security_id']
        self.account_id = result['account_id']
        self.created_at = result['created_at']
        self.updated_at = result['updated_at']
        self.order_type = result['order_type']
        self.order_sub_type = result['order_sub_type']
        self.status = result['status']
        self.is_settled = result['settled']
        self.quantity = result['quantity']
        self.limit_price = result['limit_price']['amount']
        self.filled_at = result['filled_at']
        self.fill_quantity = result['fill_quantity']
        self.market_value = result['market_value']['amount'] if result['market_value'] else 0
