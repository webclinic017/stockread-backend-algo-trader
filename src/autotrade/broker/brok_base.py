from abc import abstractmethod, ABC
from typing import Optional

from src.autotrade.broker.order import Order, OrderAction


class IBroker(ABC):

    @abstractmethod
    def bind_to_trade(self, trade):
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_live(self):
        raise NotImplementedError()

    @abstractmethod
    def market_buy(self, quantity):
        raise NotImplementedError()

    @abstractmethod
    def market_sell(self, quantity):
        raise NotImplementedError()

    @abstractmethod
    def limit_buy(self, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def limit_sell(self, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_buy(self, stop_price, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def stop_limit_sell(self, stop_price, limit_price, quantity):
        raise NotImplementedError()

    @abstractmethod
    def cancel_order(self, order):
        raise NotImplementedError()


class IBrokerLive(ABC):

    @abstractmethod
    def set_trading_account(self, trading_account_id: str):
        """
        Sets the the account to be used for trading

        :param trading_account_id:
        :type trading_account_id: str
        """
        raise NotImplementedError()

    @abstractmethod
    def find_instrument(self):
        """Returns the instrument information"""
        raise NotImplementedError()

    @abstractmethod
    def get_position(self):
        """Returns the position value"""
        raise NotImplementedError()

    @abstractmethod
    def get_pending_orders(self, order_action: Optional[OrderAction] = None):
        """Returns the position value"""
        raise NotImplementedError()

    @abstractmethod
    def update_order_info(self, order: Order):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def translate_order_status(broker_order_status: str):
        raise NotImplementedError()

    @property
    @abstractmethod
    def buying_power(self):
        """
        Returns the cash available to trade.
        """
        raise NotImplementedError()


class BaseLiveBroker:
    def __init__(self):
        self._is_live = True
        self._trade_bot = None

        # trading account & cash
        self._trading_account_id: Optional[str] = None
        self._account_cash_available: float = 0

        # trading instruments to be added
        self._trading_symbol = None
        self._currency = None
        self._ticker_id = None
        self._position = None
